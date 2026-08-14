"""Build a deterministic privacy-safe candidate catalog from historical check-ins."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from location_entropy.data import load_checkins

SENSITIVE_CATEGORY = re.compile(
    r"\b(?:home|private|residential|residence|housing|apartment|workplace|office)\b",
    re.IGNORECASE,
)
PROVENANCE = "Aggregated historical Foursquare sample"


def _rounded_count(value: int) -> int:
    return max(5, int(5 * round(value / 5)))


def _aggregate_city(path: Path, city: str, min_checkins: int, min_visitors: int) -> pd.DataFrame:
    data = load_checkins(path, city)
    data = data[~data["category_name"].str.contains(SENSITIVE_CATEGORY, na=False)]
    category_counts = (
        data.groupby(["venue_id", "category_id", "category_name"], observed=True)
        .size()
        .rename("category_checkins")
        .reset_index()
        .sort_values(
            ["venue_id", "category_checkins", "category_name", "category_id"],
            ascending=[True, False, True, True],
            kind="stable",
        )
        .drop_duplicates("venue_id", keep="first")
    )
    support = (
        data.groupby("venue_id", observed=True)
        .agg(
            checkins=("venue_id", "size"),
            visitors=("user_id", "nunique"),
        )
        .reset_index()
    )
    eligible = support.merge(category_counts, on="venue_id", validate="one_to_one")
    eligible = eligible[
        (eligible["checkins"] >= min_checkins)
        & (eligible["visitors"] >= min_visitors)
    ].copy()
    eligible = eligible.sort_values(
        ["checkins", "visitors", "category_name", "venue_id"],
        ascending=[False, False, True, True],
        kind="stable",
    ).reset_index(drop=True)
    if eligible.empty:
        return eligible
    eligible["popularity_percentile"] = (
        eligible["checkins"].rank(method="min", pct=True) * 100
    ).round().astype(int)
    return eligible


def _stratified_rows(data: pd.DataFrame, limit: int) -> pd.DataFrame:
    if len(data) <= limit:
        return data
    indices = np.linspace(0, len(data) - 1, num=limit)
    selected = sorted({int(round(index)) for index in indices})
    if len(selected) < limit:
        selected.extend(index for index in range(len(data)) if index not in selected)
    return data.iloc[selected[:limit]]


def generate_catalog(
    sources: dict[str, Path],
    *,
    min_checkins: int = 30,
    min_visitors: int = 15,
    candidates_per_city: int = 8,
) -> list[dict[str, object]]:
    """Return safe aggregate candidates; never return source record identifiers."""
    catalog: list[dict[str, object]] = []
    for city in sorted(sources):
        eligible = _aggregate_city(
            Path(sources[city]), city, min_checkins, min_visitors
        )
        selected = _stratified_rows(eligible, candidates_per_city)
        for city_index, row in enumerate(selected.itertuples(index=False), start=1):
            percentile = int(row.popularity_percentile)
            popularity = percentile / 100
            catalog.append(
                {
                    "id": f"candidate-{city.lower()}-{city_index:03d}",
                    "label": f"{city} · {row.category_name} · Candidate {city_index:02d}",
                    "city": city,
                    "category": str(row.category_name),
                    "historical_checkins": _rounded_count(int(row.checkins)),
                    "distinct_historical_visitors": _rounded_count(int(row.visitors)),
                    "aggregate_popularity_percentile": percentile,
                    "baseline_relevance": round(0.35 + 0.60 * popularity, 4),
                    "aggregate_novelty": round(1 - popularity, 4),
                    "provenance": PROVENANCE,
                }
            )
    return catalog


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nyc", type=Path, required=True)
    parser.add_argument("--tokyo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-checkins", type=int, default=30)
    parser.add_argument("--min-visitors", type=int, default=15)
    parser.add_argument("--per-city", type=int, default=8)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog = generate_catalog(
        {"NYC": args.nyc, "TKY": args.tokyo},
        min_checkins=args.min_checkins,
        min_visitors=args.min_visitors,
        candidates_per_city=args.per_city,
    )
    serialized = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        try:
            committed = args.output.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise ValueError("candidate catalog is missing") from error
        if committed != serialized:
            raise ValueError("candidate catalog is stale")
        print(f"Fresh: {args.output}")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(f"Wrote {len(catalog)} privacy-safe candidates to {args.output}")


if __name__ == "__main__":
    main()
