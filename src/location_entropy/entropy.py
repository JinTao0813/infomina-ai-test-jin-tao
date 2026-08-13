"""Vectorized Shannon entropy calculations."""

from collections.abc import Sequence

import numpy as np
import pandas as pd

METRIC_COLUMNS = [
    "observation_count",
    "unique_location_count",
    "entropy",
    "normalized_entropy",
]


def _as_group_columns(group_cols: str | Sequence[str]) -> list[str]:
    columns = [group_cols] if isinstance(group_cols, str) else list(group_cols)
    if not columns or any(not isinstance(column, str) for column in columns):
        raise ValueError("group_cols must contain at least one column name")
    if len(columns) != len(set(columns)):
        raise ValueError("group_cols must not contain duplicate column names")
    return columns


def calculate_location_entropy(
    data: pd.DataFrame,
    group_cols: str | Sequence[str],
    location_col: str,
) -> pd.DataFrame:
    """Calculate base-2 location entropy for each independent group.

    Raw entropy is reported in bits. Normalized entropy is defined as zero for
    groups with one observed location and otherwise ranges from zero to one.
    """
    groups = _as_group_columns(group_cols)
    required = [*groups, location_col]
    missing = list(
        dict.fromkeys(column for column in required if column not in data.columns)
    )
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    group_nulls = int(data[groups].isna().sum().sum())
    if group_nulls:
        raise ValueError(f"group columns contain {group_nulls} null value(s)")
    location_nulls = int(data[location_col].isna().sum())
    if location_nulls:
        raise ValueError(f"location column contains {location_nulls} null value(s)")

    output_columns = [*groups, *METRIC_COLUMNS]
    if data.empty:
        return pd.DataFrame(
            {column: pd.Series(dtype="object") for column in output_columns}
        )

    grouping_options = {"sort": False, "observed": True, "dropna": False}
    location_counts = (
        data.groupby(
            [*groups, location_col], as_index=False, **grouping_options
        )
        .size()
        .rename(columns={"size": "__location_count__"})
    )
    totals = location_counts.groupby(groups, **grouping_options)[
        "__location_count__"
    ].transform("sum")
    probabilities = location_counts["__location_count__"] / totals
    location_counts["__entropy_component__"] = -probabilities * np.log2(
        probabilities
    )

    metrics = location_counts.groupby(
        groups, as_index=False, **grouping_options
    ).agg(
        observation_count=("__location_count__", "sum"),
        unique_location_count=(location_col, "size"),
        entropy=("__entropy_component__", "sum"),
    )
    denominator = np.log2(metrics["unique_location_count"].clip(lower=1))
    metrics["normalized_entropy"] = np.where(
        metrics["unique_location_count"] > 1,
        metrics["entropy"] / denominator,
        0.0,
    )
    metrics["normalized_entropy"] = metrics["normalized_entropy"].clip(0.0, 1.0)
    return metrics[output_columns]
