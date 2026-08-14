"""Build safe synthetic profiles without reading source check-ins.

Values are fixed synthetic artifacts anchored to aggregate ranges reported in
the executed notebook. No source user IDs, coordinates, or trajectories enter
this offline build.
"""

import json
from pathlib import Path

TARGET = Path(__file__).parents[1] / "backend/api/fixtures/profiles.json"

PROFILES = [
    {
        "id": "routine",
        "label": "Routine-oriented demo",
        "venue_entropy": 0.72,
        "category_entropy": 0.58,
        "weekend_delta": 0.04,
        "observation_count": 180,
        "confidence": 0.90,
        "familiar_categories": ["Train Station", "Coffee Shop", "Building"],
    },
    {
        "id": "mixed",
        "label": "Mixed demo",
        "venue_entropy": 0.85,
        "category_entropy": 0.76,
        "weekend_delta": 0.06,
        "observation_count": 154,
        "confidence": 0.84,
        "familiar_categories": [
            "Coffee Shop",
            "Train Station",
            "Burger Joint",
            "Building",
        ],
    },
    {
        "id": "exploration",
        "label": "Exploration-oriented demo",
        "venue_entropy": 0.95,
        "category_entropy": 0.89,
        "weekend_delta": 0.08,
        "observation_count": 240,
        "confidence": 0.94,
        "familiar_categories": ["Concert Hall", "Bar", "Stadium", "Clothing Store"],
    },
    {
        "id": "sparse",
        "label": "New / sparse history demo",
        "venue_entropy": 0.62,
        "category_entropy": 0.51,
        "weekend_delta": 0.11,
        "observation_count": 8,
        "confidence": 0.12,
        "familiar_categories": ["Coffee Shop"],
    },
]


def main() -> None:
    TARGET.write_text(
        json.dumps(PROFILES, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(PROFILES)} synthetic profiles to {TARGET}")


if __name__ == "__main__":
    main()
