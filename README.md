# Location Entropy Analysis

**Author:** Jin Tao

**Email:** jintaoyap@gmail.com

This project asks whether people repeatedly check in at a small set of venues or spread their visits more widely. It compares the Foursquare TSMC 2014 NYC and Tokyo samples and looks separately at weekday and weekend activity. The executed [`location_entropy_analysis.ipynb`](notebooks/location_entropy_analysis.ipynb) contains the full analysis and explains the choices made along the way.

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

## Dataset

The assignment recommends the EPFL mobility dataset but allows another public spatio-temporal dataset. I could not access the recommended data, so I used the **Foursquare TSMC 2014 NYC and Tokyo Check-in Dataset**. Each row identifies a user, venue, and time, which is enough to calculate per-user location entropy and compare the two samples.

Download the dataset from the [dataset author's Foursquare dataset page](https://sites.google.com/site/yangdingqi/home/foursquare-dataset), extract it locally, and preserve the raw TSV files unchanged:

```text
dataset_tsmc2014/
  dataset_TSMC2014_NYC.txt
  dataset_TSMC2014_TKY.txt
  dataset_TSMC2014_readme.txt
```

`dataset_tsmc2014/` is ignored by Git. Do not convert the files to CSV or Parquet for this submission.

Expected source-file checks:

| File                       |    Rows | SHA-256                                                            |
| -------------------------- | ------: | ------------------------------------------------------------------ |
| `dataset_TSMC2014_NYC.txt` | 227,428 | `2f39ce698e5bff6683c74bec30c436cc022c160b0f3d73c5268b55491b2445f9` |
| `dataset_TSMC2014_TKY.txt` | 573,703 | `85542c605ce708d8584637756590383a84e9bbdb71342d0d8e78858ba2a0e5c8` |

The loader reads headerless TSV with Latin-1 encoding and this explicit schema:

| Column                    | Type                        |
| ------------------------- | --------------------------- |
| `user_id`                 | string                      |
| `venue_id`                | string                      |
| `category_id`             | string                      |
| `category_name`           | string                      |
| `latitude`                | float                       |
| `longitude`               | float                       |
| `timezone_offset_minutes` | integer                     |
| `utc_time`                | timezone-aware UTC datetime |

It adds `city` and a timezone-aware `local_time`. Users are keyed by `(city, user_id)` because IDs restart in each file.

## Project layout

```text
src/location_entropy/entropy.py  # reusable, vectorized entropy API
src/location_entropy/data.py     # strict loading, validation, quality report
tests/                           # hand-calculated metric and loader tests
notebooks/location_entropy_analysis.ipynb
```

## Metric API

```python
calculate_location_entropy(
    data,
    group_cols,
    location_col,
)
```

The function returns one row per group with its event count, number of locations, base-2 entropy in bits, and normalized entropy. It supports composite group keys and validates missing columns and null keys; tests cover the calculation and edge cases.

## Citation

Yang, D., Zhang, D., Zheng, V. W., & Yu, Z. (2015). Modeling User Activity Preference by Leveraging User Spatial Temporal Characteristics in LBSNs. _IEEE Transactions on Systems, Man, and Cybernetics: Systems_, 45(1), 129–142.
