from pathlib import Path

from scripts.build_candidate_catalog import generate_catalog


def _write_city(path: Path, rows: list[tuple[str, str, str, str]]) -> None:
    lines = []
    for index, (user_id, venue_id, category_id, category_name) in enumerate(rows):
        lines.append(
            "\t".join(
                [
                    user_id,
                    venue_id,
                    category_id,
                    category_name,
                    "40.7000",
                    "-73.9000",
                    "-240",
                    f"Tue Apr {1 + index % 20:02d} 12:00:00 +0000 2013",
                ]
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="latin-1")


def test_catalog_is_deterministic_supported_pseudonymous_and_safe(tmp_path: Path) -> None:
    source = tmp_path / "city.txt"
    rows: list[tuple[str, str, str, str]] = []
    rows += [(f"u{i % 4}", "popular", "cat-coffee", "Coffee Shop") for i in range(12)]
    rows += [(f"u{i % 3}", "museum", "cat-museum", "Museum") for i in range(8)]
    rows += [(f"u{i % 4}", "home", "cat-home", "Home (private)") for i in range(12)]
    rows += [("only-one-user", "rare", "cat-park", "Park") for _ in range(12)]
    _write_city(source, rows)

    first = generate_catalog(
        {"NYC": source}, min_checkins=6, min_visitors=2, candidates_per_city=4
    )
    second = generate_catalog(
        {"NYC": source}, min_checkins=6, min_visitors=2, candidates_per_city=4
    )

    assert first == second
    assert [candidate["category"] for candidate in first] == ["Coffee Shop", "Museum"]
    assert all(candidate["label"].startswith("NYC · ") for candidate in first)
    assert all("Candidate" in candidate["label"] for candidate in first)
    assert all(candidate["historical_checkins"] >= 5 for candidate in first)
    assert all(candidate["distinct_historical_visitors"] >= 2 for candidate in first)
    assert all(candidate["provenance"] == "Aggregated historical Foursquare sample" for candidate in first)

    forbidden = {
        "venue_id",
        "user_id",
        "latitude",
        "longitude",
        "coordinates",
        "timestamp",
        "utc_time",
        "trajectory",
        "name",
    }
    assert forbidden.isdisjoint({key for candidate in first for key in candidate})
    exposed_values = {str(value) for candidate in first for value in candidate.values()}
    assert {"popular", "museum", "rare", "only-one-user"}.isdisjoint(exposed_values)
