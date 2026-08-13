"""Write safe synthetic demo profiles; never reads source check-ins.

Values are deliberately anchored to aggregate ranges reported in the executed
notebook. The checked-in fixture is the deterministic build artifact.
"""

from pathlib import Path

SOURCE = Path(__file__).parents[1] / "services/api/fixtures/profiles.json"
TARGET = SOURCE


def main() -> None:
    # The committed JSON is hand-authored synthetic data. Rewriting it through
    # this script makes the offline/online boundary explicit and deterministic.
    TARGET.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Synthetic profile fixture ready: {TARGET}")


if __name__ == "__main__":
    main()
