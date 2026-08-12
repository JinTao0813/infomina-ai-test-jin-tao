"""Vectorized Shannon entropy calculations."""

from collections.abc import Sequence
from numbers import Real

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

METRIC_COLUMNS = [
    "observation_count",
    "total_weight",
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


def _validate_log_base(log_base: float) -> float:
    base = (
        float(log_base)
        if isinstance(log_base, Real) and not isinstance(log_base, bool)
        else np.nan
    )
    if not np.isfinite(base) or base <= 0 or base == 1:
        raise ValueError(
            "log_base must be a finite number greater than 0 and not equal to 1"
        )
    return base


def calculate_location_entropy(
    data: pd.DataFrame,
    group_cols: str | Sequence[str],
    location_col: str,
    weight_col: str | None = None,
    log_base: float = np.e,
) -> pd.DataFrame:
    """Calculate Shannon entropy of observed locations for independent groups.

    ``observation_count`` counts input rows. With weights, ``total_weight`` is
    their sum and ``unique_location_count`` counts only locations with positive
    aggregate weight. Groups whose total weight is zero are retained with zero
    locations and zero entropy.
    """
    groups = _as_group_columns(group_cols)
    base = _validate_log_base(log_base)
    required = [*groups, location_col, *([weight_col] if weight_col else [])]
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

    frame = data[[*groups, location_col]].copy()
    internal_weight = "__entropy_weight__"
    while internal_weight in frame.columns:
        internal_weight = f"_{internal_weight}"

    if weight_col is None:
        frame[internal_weight] = 1.0
    else:
        weights = data[weight_col]
        if is_bool_dtype(weights.dtype) or not is_numeric_dtype(weights.dtype):
            raise ValueError(f"weight column '{weight_col}' must be numeric")
        null_or_nonfinite = weights.isna() | ~np.isfinite(weights)
        if null_or_nonfinite.any():
            count = int(null_or_nonfinite.sum())
            raise ValueError(
                f"weight column '{weight_col}' must be finite; found {count} invalid value(s)"
            )
        negative = weights < 0
        if negative.any():
            count = int(negative.sum())
            raise ValueError(
                f"weight column '{weight_col}' has negative values; found {count}"
            )
        frame[internal_weight] = weights.astype(float)

    grouping_options = {"sort": False, "observed": True, "dropna": False}
    summaries = frame.groupby(groups, as_index=False, **grouping_options).agg(
        observation_count=(location_col, "size"),
        total_weight=(internal_weight, "sum"),
    )
    location_weights = frame.groupby(
        [*groups, location_col], as_index=False, **grouping_options
    )[internal_weight].sum()
    positive = location_weights[location_weights[internal_weight] > 0].copy()

    if positive.empty:
        metrics = summaries.copy()
        metrics["unique_location_count"] = 0
        metrics["entropy"] = 0.0
    else:
        totals = summaries[[*groups, "total_weight"]]
        positive = positive.merge(totals, on=groups, how="left", validate="many_to_one")
        probabilities = positive[internal_weight] / positive["total_weight"]
        positive["__entropy_component__"] = -(
            probabilities * np.log(probabilities) / np.log(base)
        )
        distribution = positive.groupby(groups, as_index=False, **grouping_options).agg(
            unique_location_count=(location_col, "size"),
            entropy=("__entropy_component__", "sum"),
        )
        metrics = summaries.merge(
            distribution, on=groups, how="left", validate="one_to_one"
        )
        metrics["unique_location_count"] = (
            metrics["unique_location_count"].fillna(0).astype(int)
        )
        metrics["entropy"] = metrics["entropy"].fillna(0.0)

    denominator = np.log(metrics["unique_location_count"].clip(lower=1)) / np.log(base)
    metrics["normalized_entropy"] = np.where(
        metrics["unique_location_count"] > 1,
        metrics["entropy"] / denominator,
        0.0,
    )
    metrics["normalized_entropy"] = metrics["normalized_entropy"].clip(0.0, 1.0)
    return metrics[output_columns]
