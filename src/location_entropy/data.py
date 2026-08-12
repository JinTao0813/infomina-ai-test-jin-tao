"""Strict loading, validation, and quality summaries for TSMC 2014 data."""

from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pandas as pd

SOURCE_COLUMNS = [
    "user_id",
    "venue_id",
    "category_id",
    "category_name",
    "latitude",
    "longitude",
    "timezone_offset_minutes",
    "utc_time",
]


@dataclass(frozen=True)
class CityConfiguration:
    """Time interpretation rules for one dataset partition."""

    timezone: str
    expected_offsets: frozenset[int]


CITY_CONFIGS = {
    "NYC": CityConfiguration("America/New_York", frozenset({-300, -240})),
    "TKY": CityConfiguration("Asia/Tokyo", frozenset({540})),
}

SOURCE_DTYPES = {
    "user_id": "string",
    "venue_id": "string",
    "category_id": "string",
    "category_name": "string",
    "latitude": "float64",
    "longitude": "float64",
    "timezone_offset_minutes": "Int64",
    "utc_time": "string",
}


@dataclass(frozen=True)
class ActivitySummary:
    """Per-user activity range for one preparation stage."""

    minimum: int
    median: float
    maximum: int


@dataclass(frozen=True)
class CityQualityReport:
    """Aggregate, non-identifying checks for one city file."""

    city: str
    raw_rows: int
    clean_rows: int
    exact_duplicates: int
    users: int
    venues: int
    categories: int
    category_ids: int
    malformed_rows: int
    blank_fields: int
    invalid_coordinate_rows: int
    home_private_checkins: int
    inconsistent_timezone_rows: int
    venue_category_conflicts: int
    venue_coordinate_conflicts: int
    raw_activity: ActivitySummary
    clean_activity: ActivitySummary


def _validate_city(city: str) -> str:
    normalized = city.upper() if isinstance(city, str) else city
    if normalized not in CITY_CONFIGS:
        raise ValueError(f"city must be one of {sorted(CITY_CONFIGS)}")
    return normalized


def _invalid_coordinate_mask(data: pd.DataFrame) -> pd.Series:
    return ~data["latitude"].between(-90, 90) | ~data["longitude"].between(-180, 180)


def _summarize_activity(activity: pd.Series) -> ActivitySummary:
    return ActivitySummary(
        minimum=int(activity.min()),
        median=float(activity.median()),
        maximum=int(activity.max()),
    )


def _count_malformed_rows(path: Path) -> int:
    expected_tabs = len(SOURCE_COLUMNS) - 1
    with path.open("rb") as rows:
        return sum(row.count(b"\t") != expected_tabs for row in rows)


def _drop_exact_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    return data.drop_duplicates(subset=SOURCE_COLUMNS, keep="first")


def load_checkins(path: str | Path, city: str) -> pd.DataFrame:
    """Load one headerless Latin-1 TSV and derive authoritative local time."""
    normalized_city = _validate_city(city)
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Check-in file not found: {source}")

    malformed_rows = _count_malformed_rows(source)
    if malformed_rows:
        raise ValueError(f"malformed TSV field count in {malformed_rows} row(s)")

    try:
        data = pd.read_csv(  # ty: ignore[no-matching-overload]
            source,
            sep="\t",
            encoding="latin-1",
            header=None,
            names=SOURCE_COLUMNS,
            dtype=SOURCE_DTYPES,
            on_bad_lines="error",
        )
    except (pd.errors.ParserError, TypeError, ValueError) as error:
        raise ValueError(
            f"Could not parse expected 8-column TSV schema: {error}"
        ) from error

    null_counts = data[SOURCE_COLUMNS].isna().sum()
    blank_strings = {
        column: int(data[column].str.strip().eq("").sum())
        for column in [
            "user_id",
            "venue_id",
            "category_id",
            "category_name",
            "utc_time",
        ]
    }
    invalid_fields = {
        column: int(null_counts[column]) + blank_strings.get(column, 0)
        for column in SOURCE_COLUMNS
        if int(null_counts[column]) + blank_strings.get(column, 0) > 0
    }
    if invalid_fields:
        details = ", ".join(
            f"{column}={count}" for column, count in invalid_fields.items()
        )
        raise ValueError(f"blank or null required fields: {details}")

    invalid_coordinates = _invalid_coordinate_mask(data)
    if invalid_coordinates.any():
        raise ValueError(
            f"coordinate validation failed for {int(invalid_coordinates.sum())} row(s)"
        )

    parsed_utc = pd.to_datetime(
        data["utc_time"],
        format="%a %b %d %H:%M:%S %z %Y",
        errors="coerce",
        utc=True,
    )
    if parsed_utc.isna().any():
        raise ValueError(
            f"utc_time parsing failed for {int(parsed_utc.isna().sum())} row(s)"
        )

    data["timezone_offset_minutes"] = data["timezone_offset_minutes"].astype("int64")
    data["utc_time"] = parsed_utc
    data["city"] = normalized_city
    data["local_time"] = parsed_utc.dt.tz_convert(
        CITY_CONFIGS[normalized_city].timezone
    )
    data.attrs["malformed_rows"] = malformed_rows
    return data[[*SOURCE_COLUMNS, "city", "local_time"]]


def summarize_checkins(data: pd.DataFrame) -> CityQualityReport:
    """Compute aggregate quality checks without exposing users or coordinates."""
    missing = [
        column
        for column in [*SOURCE_COLUMNS, "city", "local_time"]
        if column not in data
    ]
    if missing:
        raise ValueError(f"Missing required columns for quality report: {missing}")
    cities = data["city"].drop_duplicates().tolist()
    if len(cities) != 1:
        raise ValueError("Quality reports require exactly one city")
    city = _validate_city(cities[0])

    clean = _drop_exact_duplicates(data)
    exact_duplicates = len(data) - len(clean)
    raw_activity = cast(pd.Series, data.groupby("user_id", observed=True).size())
    clean_activity = cast(pd.Series, clean.groupby("user_id", observed=True).size())
    category_variants = (
        clean[["venue_id", "category_id"]].drop_duplicates().groupby("venue_id").size()
    )
    coordinate_variants = (
        clean[["venue_id", "latitude", "longitude"]]
        .drop_duplicates()
        .groupby("venue_id")
        .size()
    )
    blank_fields = int(data[SOURCE_COLUMNS].isna().sum().sum())
    invalid_coordinates = int(_invalid_coordinate_mask(data).sum())

    return CityQualityReport(
        city=city,
        raw_rows=len(data),
        clean_rows=len(clean),
        exact_duplicates=exact_duplicates,
        users=int(clean["user_id"].nunique()),
        venues=int(clean["venue_id"].nunique()),
        categories=int(clean["category_name"].nunique()),
        category_ids=int(clean["category_id"].nunique()),
        malformed_rows=int(data.attrs.get("malformed_rows", 0)),
        blank_fields=blank_fields,
        invalid_coordinate_rows=invalid_coordinates,
        home_private_checkins=int((data["category_name"] == "Home (private)").sum()),
        inconsistent_timezone_rows=int(
            (
                ~data["timezone_offset_minutes"].isin(
                    CITY_CONFIGS[city].expected_offsets
                )
            ).sum()
        ),
        venue_category_conflicts=int((category_variants > 1).sum()),
        venue_coordinate_conflicts=int((coordinate_variants > 1).sum()),
        raw_activity=_summarize_activity(raw_activity),
        clean_activity=_summarize_activity(clean_activity),
    )


def prepare_city_data(
    path: str | Path, city: str
) -> tuple[pd.DataFrame, CityQualityReport]:
    """Load, validate, report, and remove exact duplicate source rows."""
    raw = load_checkins(path, city)
    report = summarize_checkins(raw)
    clean = _drop_exact_duplicates(raw).reset_index(drop=True)
    return clean, report
