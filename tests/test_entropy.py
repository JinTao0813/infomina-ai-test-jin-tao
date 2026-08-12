import math

import numpy as np
import pandas as pd
import pytest

from location_entropy.entropy import calculate_location_entropy

METRICS = [
    "observation_count",
    "total_weight",
    "unique_location_count",
    "entropy",
    "normalized_entropy",
]


def test_one_location_has_zero_entropy() -> None:
    data = pd.DataFrame({"user": ["a", "a", "a"], "venue": ["x", "x", "x"]})

    result = calculate_location_entropy(data, "user", "venue")

    assert result.loc[0, "observation_count"] == 3
    assert result.loc[0, "total_weight"] == 3
    assert result.loc[0, "unique_location_count"] == 1
    assert result.loc[0, "entropy"] == pytest.approx(0.0)
    assert result.loc[0, "normalized_entropy"] == pytest.approx(0.0)


def test_uniform_locations_have_log_k_entropy_and_unit_normalized_entropy() -> None:
    data = pd.DataFrame({"user": ["a"] * 6, "venue": ["x", "y", "z"] * 2})

    result = calculate_location_entropy(data, "user", "venue")

    assert result.loc[0, "entropy"] == pytest.approx(math.log(3))
    assert result.loc[0, "normalized_entropy"] == pytest.approx(1.0)


def test_unequal_distribution_matches_hand_calculation() -> None:
    data = pd.DataFrame({"user": ["a"] * 4, "venue": ["x", "x", "x", "y"]})
    expected = -(0.75 * math.log(0.75) + 0.25 * math.log(0.25))

    result = calculate_location_entropy(data, "user", "venue")

    assert result.loc[0, "entropy"] == pytest.approx(expected)
    assert result.loc[0, "normalized_entropy"] == pytest.approx(expected / math.log(2))


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
    assert result.loc[("NYC", "1"), "entropy"] == pytest.approx(math.log(2))
    assert result.loc[("TKY", "1"), "entropy"] == pytest.approx(0.0)
    assert result.loc[("TKY", "2"), "observation_count"] == 1


def test_weighted_entropy_uses_summed_weights() -> None:
    data = pd.DataFrame(
        {"user": ["a", "a", "a"], "venue": ["x", "x", "y"], "minutes": [1.0, 2.0, 1.0]}
    )
    expected = -(0.75 * math.log(0.75) + 0.25 * math.log(0.25))

    result = calculate_location_entropy(data, "user", "venue", weight_col="minutes")

    assert result.loc[0, "observation_count"] == 3
    assert result.loc[0, "total_weight"] == pytest.approx(4.0)
    assert result.loc[0, "entropy"] == pytest.approx(expected)


@pytest.mark.parametrize(("base", "expected_entropy"), [(2.0, 2.0), (0.5, -2.0)])
def test_configurable_log_base(base: float, expected_entropy: float) -> None:
    data = pd.DataFrame({"user": ["a"] * 4, "venue": ["x", "y", "z", "w"]})

    result = calculate_location_entropy(data, "user", "venue", log_base=base)

    assert result.loc[0, "entropy"] == pytest.approx(expected_entropy)
    assert result.loc[0, "normalized_entropy"] == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {"group_cols": "missing", "location_col": "venue"},
            "Missing required columns.*missing",
        ),
        (
            {"group_cols": "user", "location_col": "missing"},
            "Missing required columns.*missing",
        ),
        (
            {"group_cols": "user", "location_col": "venue", "weight_col": "missing"},
            "Missing required columns.*missing",
        ),
    ],
)
def test_missing_columns_fail_clearly(kwargs: dict[str, object], message: str) -> None:
    data = pd.DataFrame({"user": ["a"], "venue": ["x"]})

    with pytest.raises(ValueError, match=message):
        calculate_location_entropy(data, **kwargs)


@pytest.mark.parametrize(
    ("column", "message"), [("user", "group.*1 null"), ("venue", "location.*1 null")]
)
def test_null_keys_fail_with_counts(column: str, message: str) -> None:
    data = pd.DataFrame({"user": ["a", "b"], "venue": ["x", "y"]})
    data.loc[0, column] = None

    with pytest.raises(ValueError, match=message):
        calculate_location_entropy(data, "user", "venue")


@pytest.mark.parametrize(
    ("weights", "message"),
    [
        ([1, "bad"], "numeric"),
        ([1.0, -1.0], "negative.*1"),
        ([1.0, np.inf], "finite.*1"),
        ([1.0, np.nan], "finite.*1"),
    ],
)
def test_invalid_weights_fail_clearly(weights: list[object], message: str) -> None:
    data = pd.DataFrame({"user": ["a", "a"], "venue": ["x", "y"], "weight": weights})

    with pytest.raises(ValueError, match=message):
        calculate_location_entropy(data, "user", "venue", weight_col="weight")


@pytest.mark.parametrize("base", [0, -2, 1, np.nan, np.inf, "two"])
def test_invalid_log_bases_fail(base: object) -> None:
    data = pd.DataFrame({"user": ["a"], "venue": ["x"]})

    with pytest.raises(ValueError, match="log_base"):
        calculate_location_entropy(data, "user", "venue", log_base=base)


def test_empty_input_returns_documented_schema() -> None:
    data = pd.DataFrame(columns=["city", "user", "venue"])

    result = calculate_location_entropy(data, ["city", "user"], "venue")

    assert result.empty
    assert list(result.columns) == ["city", "user", *METRICS]


def test_zero_weights_are_ignored_and_zero_total_group_is_retained() -> None:
    data = pd.DataFrame(
        {
            "user": ["a", "a", "a", "b", "b"],
            "venue": ["x", "y", "y", "x", "z"],
            "weight": [0.0, 1.0, 1.0, 0.0, 0.0],
        }
    )

    result = calculate_location_entropy(data, "user", "venue", "weight").set_index(
        "user"
    )

    assert result.loc["a", "observation_count"] == 3
    assert result.loc["a", "unique_location_count"] == 1
    assert result.loc["a", "entropy"] == pytest.approx(0.0)
    assert result.loc["b", "observation_count"] == 2
    assert result.loc["b", "total_weight"] == pytest.approx(0.0)
    assert result.loc["b", "unique_location_count"] == 0
    assert result.loc["b", "entropy"] == pytest.approx(0.0)
    assert result.loc["b", "normalized_entropy"] == pytest.approx(0.0)
