# Resources for the Location Entropy Interview

These are the sources I would return to when I need to check a fact or strengthen an explanation. Repository files come first for claims about this project; external sources provide the original data, theory, and library behavior.

## Project and theory

- [Assignment: `AI_Interview_DS_Entropy.pdf`](../AI_Interview_DS_Entropy.pdf)  
  The original brief and the four capacities the interviewer wants to see.
- [Executed analysis notebook](../notebooks/location_entropy_analysis.ipynb)  
  The actual methodology, figures, numerical results, interpretations, and product proposal.
- [Repository overview](../README.md) and [product boundaries](../PRODUCT.md)  
  Current architecture, run commands, claim boundary, scope, and terminology.
- [Entropy implementation](../src/location_entropy/entropy.py)  
  The exact three-argument metric contract, validation, vectorized calculation, and output columns.
- [Data implementation](../src/location_entropy/data.py)  
  Parsing, quality checks, timezone handling, duplicate removal, and reporting.
- [Metric tests](../tests/test_entropy.py) and [loader tests](../tests/test_data.py)  
  Hand-calculated examples and executable edge cases.
- [Deterministic ranker](../backend/api/ranking.py), [API](../backend/api/main.py), and [schemas](../backend/api/schemas.py)  
  Applied-discovery policy, candidate scoring, safe response contract, sparse fallback, and local service boundary.
- [Candidate catalog generator](../scripts/build_candidate_catalog.py)  
  Sensitive-category exclusion, support thresholds, deterministic sampling, pseudonymization, and rounded aggregates.
- [Notebook presentation exporter](../scripts/export_notebook_presentation.py)  
  Safe static artifact generation, active-content rejection, source fingerprints, and freshness checks.
- [Discovery frontend](../apps/frontend/components/discovery-experience.tsx) and [analysis renderer](../apps/frontend/components/analysis-case-study.tsx)  
  Accessible interaction states and the static notebook-derived case-study route.
- [Backend/export tests](../tests/test_api.py), [catalog tests](../tests/test_candidate_catalog.py), [frontend tests](../apps/frontend/components/discovery-experience.test.tsx), and [analysis-renderer tests](../apps/frontend/components/analysis-case-study.test.tsx)  
  Current automated evidence: 36 Python and 6 frontend test cases.
- [StatQuest: “Entropy (for data science) Clearly Explained”](https://www.youtube.com/watch?v=YtebGVx-Fxw)  
  My introduction to entropy. It explains surprise and expected surprise before arriving at the formula used in this project.
- [Shannon, “A Mathematical Theory of Communication”](https://ieeexplore.ieee.org/document/6773024)  
  The foundational source for Shannon entropy and the meaning of bits.

## Dataset

- [Dataset author's Foursquare page](https://sites.google.com/site/yangdingqi/home/foursquare-dataset)  
  Dataset provenance and download location.
- [Yang et al., “Modeling User Activity Preference…”](https://ieeexplore.ieee.org/document/6844862)  
  The peer-reviewed paper associated with the TSMC dataset.

## Libraries and statistical choices

- [pandas `DataFrame.groupby`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)  
  The split–apply–combine operations behind the vectorized implementation.
- [pandas time-series guide](https://pandas.pydata.org/docs/user_guide/timeseries.html) and [`Series.dt.tz_convert`](https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.tz_convert.html)  
  UTC parsing and conversion to city-local time.
- [Python `zoneinfo`](https://docs.python.org/3/library/zoneinfo.html)  
  Named IANA timezones and daylight-saving behavior.
- [NumPy `Generator.choice`](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html)  
  Sampling with replacement in the notebook's bootstrap.
- [SciPy bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)  
  A useful reference for interpreting bootstrap intervals.
- [Penn State: independent and paired samples](https://online.stat.psu.edu/stat200/lesson/1/1.4/1.4.3)  
  Why weekday and weekend observations should be compared within the same user.
- [Penn State: observational versus controlled studies](https://online.stat.psu.edu/stat509/lesson/3/3.2)  
  Why this analysis cannot establish causation.
- [pytest assertions](https://docs.pytest.org/en/stable/how-to/assert.html)  
  `pytest.approx` and floating-point comparisons.
- [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)  
  The reproducible environment and `--frozen` behavior.
- [ICO data-minimisation guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-for-the-use-of-personal-data-in-political-campaigning-1/purpose-limitation-data-minimisation-and-storage-limitation)  
  Support for the proposal's retention, purpose, and minimisation safeguards.

## Places to test my reasoning

- [Cross Validated](https://stats.stackexchange.com/) for questions about entropy normalization, bootstrap interpretation, and observational claims.
- [Data Science Stack Exchange](https://datascience.stackexchange.com/) for production metric design and recommender experiments.
- A trusted data scientist or mock interviewer for direct feedback on unclear explanations or overclaiming.

## Gaps I should be ready to discuss

- The choice of 20 check-ins per context is pragmatic; the notebook does not include a threshold sensitivity analysis.
- Prototype confidence values and ranking weights are illustrative and hand-designed, not learned or calibrated.
- Aggregate popularity is transformed into an illustrative baseline; it is not true user relevance.
- There is no production traffic, effectiveness baseline, power calculation, current venue feed, or privacy review. The implemented prototype remains a hypothesis.
