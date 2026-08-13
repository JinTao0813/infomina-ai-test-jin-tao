import math

import pandas as pd
import pytest

from location_entropy.entropy import calculate_location_entropy

METRICS = [
    "observation_count",
    "unique_location_count",
    "entropy",
    "normalized_entropy",
]


def test_one_location_has_zero_entropy() -> None:
    data = pd.DataFrame({"user": ["a", "a", "a"], "venue": ["x", "x", "x"]})

    result = calculate_location_entropy(data, "user", "venue")

    assert result.loc[0, "observation_count"] == 3
    assert result.loc[0, "unique_location_count"] == 1
    assert result.loc[0, "entropy"] == pytest.approx(0.0)
    assert result.loc[0, "normalized_entropy"] == pytest.approx(0.0)


def test_uniform_locations_have_log2_k_entropy_and_unit_normalized_entropy() -> None:
    data = pd.DataFrame({"user": ["a"] * 6, "venue": ["x", "y", "z"] * 2})

    result = calculate_location_entropy(data, "user", "venue")

    assert result.loc[0, "entropy"] == pytest.approx(math.log2(3))
    assert result.loc[0, "normalized_entropy"] == pytest.approx(1.0)


def test_unequal_distribution_matches_hand_calculation() -> None:
    data = pd.DataFrame({"user": ["a"] * 4, "venue": ["x", "x", "x", "y"]})
    expected = -(0.75 * math.log2(0.75) + 0.25 * math.log2(0.25))

    result = calculate_location_entropy(data, "user", "venue")

    assert result.loc[0, "entropy"] == pytest.approx(expected)
    assert result.loc[0, "normalized_entropy"] == pytest.approx(expected)


def test_multiple_composite_groups_are_isolated() -> None:
    data = pd.DataFrame(
        {
            "city": ["NYC", "NYC", "TKY", "TKY", "TKY"],
            "user": ["1", "1", "1", "1", "2"],
            "venue": ["x", "y", "x", "x", "z"],
        }
    )

    result = calculate_location_entropy(data, ["city", "user"], "venue").set_index(
        ["city", "user"]
    )

    assert len(result) == 3
    assert result.loc[("NYC", "1"), "entropy"] == pytest.approx(1.0)
    assert result.loc[("TKY", "1"), "entropy"] == pytest.approx(0.0)
    assert result.loc[("TKY", "2"), "observation_count"] == 1


@pytest.mark.parametrize(
    ("group_cols", "location_col"),
    [("missing", "venue"), ("user", "missing")],
)
def test_missing_columns_fail_clearly(
    group_cols: str, location_col: str
) -> None:
    data = pd.DataFrame({"user": ["a"], "venue": ["x"]})

    with pytest.raises(ValueError, match="Missing required columns.*missing"):
        calculate_location_entropy(data, group_cols, location_col)


@pytest.mark.parametrize(
    ("column", "message"), [("user", "group.*1 null"), ("venue", "location.*1 null")]
)
def test_null_keys_fail_with_counts(column: str, message: str) -> None:
    data = pd.DataFrame({"user": ["a", "b"], "venue": ["x", "y"]})
    data.loc[0, column] = None

    with pytest.raises(ValueError, match=message):
        calculate_location_entropy(data, "user", "venue")


def test_empty_input_returns_documented_schema() -> None:
    data = pd.DataFrame(columns=["city", "user", "venue"])

    result = calculate_location_entropy(data, ["city", "user"], "venue")

    assert result.empty
    assert list(result.columns) == ["city", "user", *METRICS]
