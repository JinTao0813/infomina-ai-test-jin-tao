from pathlib import Path

import pandas as pd
import pytest

from location_entropy.data import (
    SOURCE_COLUMNS,
    load_checkins,
    prepare_city_data,
    summarize_checkins,
)


def make_checkin_tsv_row(
    user: str = "1",
    venue: str = "v1",
    category: str = "c1",
    category_name: str = "Café",
    latitude: float = 40.7,
    longitude: float = -74.0,
    offset: int = -240,
    utc_time: str = "Tue Apr 03 18:00:09 +0000 2012",
) -> str:
    return "\t".join(
        map(
            str,
            [
                user,
                venue,
                category,
                category_name,
                latitude,
                longitude,
                offset,
                utc_time,
            ],
        )
    )


def write_tsv(path: Path, rows: list[str]) -> Path:
    path.write_bytes(("\n".join(rows) + "\n").encode("latin-1"))
    return path


def test_loader_uses_explicit_schema_and_timezone_aware_city_time(
    tmp_path: Path,
) -> None:
    path = write_tsv(tmp_path / "nyc.txt", [make_checkin_tsv_row()])

    result = load_checkins(path, "NYC")

    assert list(result.columns) == [*SOURCE_COLUMNS, "city", "local_time"]
    assert result.loc[0, "user_id"] == "1"
    assert result.loc[0, "category_name"] == "Café"
    assert str(result["utc_time"].dtype) == "datetime64[ns, UTC]"
    assert str(result["local_time"].dt.tz) == "America/New_York"
    assert result.loc[0, "local_time"].hour == 14


def test_tokyo_local_time_uses_city_timezone_not_supplied_offset(
    tmp_path: Path,
) -> None:
    path = write_tsv(tmp_path / "tky.txt", [make_checkin_tsv_row(offset=-999)])

    result = load_checkins(path, "TKY")

    assert str(result["local_time"].dt.tz) == "Asia/Tokyo"
    assert result.loc[0, "local_time"].hour == 3
    assert result.loc[0, "local_time"].day == 4


def test_prepare_removes_exact_duplicates_and_reports_quality(tmp_path: Path) -> None:
    duplicate = make_checkin_tsv_row()
    conflict = make_checkin_tsv_row(
        user="2", venue="v1", category="c2", category_name="Library", latitude=40.8
    )
    path = write_tsv(tmp_path / "nyc.txt", [duplicate, duplicate, conflict])

    clean, report = prepare_city_data(path, "NYC")

    assert len(clean) == 2
    assert report.raw_rows == 3
    assert report.clean_rows == 2
    assert report.exact_duplicates == 1
    assert report.users == 2
    assert report.venues == 1
    assert report.categories == 2
    assert report.category_ids == 2
    assert report.venue_category_conflicts == 1
    assert report.venue_coordinate_conflicts == 1
    assert report.inconsistent_timezone_rows == 0
    assert report.malformed_rows == 0
    assert report.raw_activity.maximum == 2
    assert report.clean_activity.maximum == 1


def test_summary_reports_activity_private_home_and_bad_offsets(tmp_path: Path) -> None:
    rows = [
        make_checkin_tsv_row(user="1", category_name="Home (private)"),
        make_checkin_tsv_row(user="1", venue="v2", offset=60),
        make_checkin_tsv_row(user="2", venue="v3"),
    ]
    data = load_checkins(write_tsv(tmp_path / "nyc.txt", rows), "NYC")

    report = summarize_checkins(data)

    assert report.home_private_checkins == 1
    assert report.inconsistent_timezone_rows == 1
    assert report.raw_activity.minimum == 1
    assert report.raw_activity.median == pytest.approx(1.5)
    assert report.raw_activity.maximum == 2
    assert report.clean_activity.minimum == 1
    assert report.clean_activity.median == pytest.approx(1.5)
    assert report.clean_activity.maximum == 2


@pytest.mark.parametrize(
    ("bad_row", "message"),
    [
        (make_checkin_tsv_row(user=""), "blank or null.*user_id"),
        (make_checkin_tsv_row(latitude=100), "coordinate"),
        (make_checkin_tsv_row(utc_time="not a date"), "utc_time"),
        (make_checkin_tsv_row() + "\textra", "malformed"),
    ],
)
def test_loader_rejects_invalid_data(
    tmp_path: Path, bad_row: str, message: str
) -> None:
    path = write_tsv(tmp_path / "bad.txt", [bad_row])

    with pytest.raises(ValueError, match=message):
        load_checkins(path, "NYC")


def test_loader_rejects_unknown_city(tmp_path: Path) -> None:
    path = write_tsv(tmp_path / "data.txt", [make_checkin_tsv_row()])

    with pytest.raises(ValueError, match="city"):
        load_checkins(path, "London")


def test_city_column_keeps_overlapping_user_ids_distinct(tmp_path: Path) -> None:
    nyc = load_checkins(
        write_tsv(tmp_path / "nyc.txt", [make_checkin_tsv_row(user="1")]), "NYC"
    )
    tky = load_checkins(
        write_tsv(
            tmp_path / "tky.txt",
            [
                make_checkin_tsv_row(
                    user="1", latitude=35.6, longitude=139.7, offset=540
                )
            ],
        ),
        "TKY",
    )

    combined = pd.concat([nyc, tky], ignore_index=True)

    assert combined[["city", "user_id"]].drop_duplicates().shape[0] == 2
