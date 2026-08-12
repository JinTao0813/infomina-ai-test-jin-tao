# Location Entropy Analysis

Reproducible analysis of venue-visiting diversity in the Foursquare TSMC 2014 NYC and Tokyo check-in samples. The primary report is the executed notebook at [`notebooks/location_entropy_analysis.ipynb`](notebooks/location_entropy_analysis.ipynb).

## Setup

Requires Python 3.11+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync --frozen
uv run pytest
```

Open the executed report:

```bash
uv run jupyter lab notebooks/location_entropy_analysis.ipynb
```

Re-execute it end to end from the repository root:

```bash
uv run jupyter nbconvert \
  --to notebook --execute notebooks/location_entropy_analysis.ipynb \
  --output location_entropy_analysis.ipynb --output-dir notebooks \
  --ExecutePreprocessor.timeout=600
```

Runtime depends on the machine and is intentionally not promised.

## Dataset

Download **NYC and Tokyo Check-in Dataset** from the [dataset author's Foursquare dataset page](https://sites.google.com/site/yangdingqi/home/foursquare-dataset), extract it locally, and preserve the raw TSV files unchanged:

```text
dataset_tsmc2014/
  dataset_TSMC2014_NYC.txt
  dataset_TSMC2014_TKY.txt
  dataset_TSMC2014_readme.txt
```

`dataset_tsmc2014/` is ignored by Git. Do not convert the files to CSV or Parquet for this submission.

Expected source-file checks:

| File | Rows | SHA-256 |
|---|---:|---|
| `dataset_TSMC2014_NYC.txt` | 227,428 | `2f39ce698e5bff6683c74bec30c436cc022c160b0f3d73c5268b55491b2445f9` |
| `dataset_TSMC2014_TKY.txt` | 573,703 | `85542c605ce708d8584637756590383a84e9bbdb71342d0d8e78858ba2a0e5c8` |

The loader reads headerless TSV with Latin-1 encoding and this explicit schema:

| Column | Type |
|---|---|
| `user_id` | string |
| `venue_id` | string |
| `category_id` | string |
| `category_name` | string |
| `latitude` | float |
| `longitude` | float |
| `timezone_offset_minutes` | integer |
| `utc_time` | timezone-aware UTC datetime |

It adds `city` and a timezone-aware `local_time`. Users are keyed by `(city, user_id)` because IDs restart in each file.

## Project layout

```text
src/location_entropy/entropy.py  # reusable, vectorized entropy API
src/location_entropy/data.py     # strict loading, validation, quality report
tests/                           # hand-calculated metric and loader tests
notebooks/location_entropy_analysis.ipynb
SPEC.md
```

## Metric API

```python
calculate_location_entropy(
    data,
    group_cols,
    location_col,
    weight_col=None,
    log_base=np.e,
)
```

Returns group keys, `observation_count`, `total_weight`, `unique_location_count`, `entropy`, and `normalized_entropy`. It validates required columns, null keys, weights, and log bases; see tests for the full contract.

## Citation

Yang, D., Zhang, D., Zheng, V. W., & Yu, Z. (2015). Modeling User Activity Preference by Leveraging User Spatial Temporal Characteristics in LBSNs. *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, 45(1), 129–142.
