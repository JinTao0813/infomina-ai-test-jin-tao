# Location Entropy Analysis — Decision and Implementation Notes

## 1. What I am building

The goal is a reproducible interview submission that calculates location entropy for each user in the Foursquare NYC and Tokyo data. The executed notebook is the main report; small source modules and tests keep the loading and metric code reusable.

A complete submission should show four things:

1. The metric is understood and calculated correctly.
2. The data are checked before the metric is trusted.
3. The findings are explained without claiming more than the data support.
4. At least one product idea follows from the findings and can be tested.

The executed notebook remains the authoritative analysis. A bounded companion application demonstrates one deterministic product hypothesis; it is not a trained or validated recommender or a live data pipeline.

## 2. Constraints

- Authoritative requirements: `AI_Interview_DS_Entropy.pdf`
- Language: Python
- Target Python: `>=3.11`
- Timebox: no more than approximately five hours
- Deadline: Saturday, 5:00 PM, as communicated by the interviewer
- Optimize for correctness, clarity, reproducibility, and judgment—not feature volume.

## 3. Main analytical question

> How concentrated or diverse are users' venue-visiting patterns, and how do those patterns vary by city and weekday/weekend context?

Do not pre-commit to conclusions. Treat expected relationships as questions or hypotheses until supported by computed results.

## 4. Dataset

### 4.1 Source files

Use the downloaded Foursquare TSMC 2014 files:

- `dataset_tsmc2014/dataset_TSMC2014_NYC.txt`
- `dataset_tsmc2014/dataset_TSMC2014_TKY.txt`
- `dataset_tsmc2014/dataset_TSMC2014_readme.txt`

The data files are headerless, Latin-1 encoded TSV files. Do not convert them to CSV or Parquet for this assignment. Preserve raw files unchanged.

### 4.2 Schema

| Column | Type | Meaning |
|---|---|---|
| `user_id` | string | Anonymized, city-local user identifier |
| `venue_id` | string | Foursquare venue identifier |
| `category_id` | string | Foursquare venue-category identifier |
| `category_name` | string | Human-readable venue category |
| `latitude` | float | Venue latitude |
| `longitude` | float | Venue longitude |
| `timezone_offset_minutes` | integer | Supplied offset from UTC |
| `utc_time` | datetime | Check-in time in UTC |

Add a `city` column during loading. Use `(city, user_id)` as the user key because user IDs restart in each file and must not be joined across cities.

### 4.3 Verified dataset facts

| Fact | NYC | Tokyo |
|---|---:|---:|
| Rows before deduplication | 227,428 | 573,703 |
| Users | 1,083 | 2,293 |
| Venues | 38,333 | 61,858 |
| Venue categories | 251 | 247 |
| Exact duplicate rows | 250 | 577 |
| Minimum check-ins per user | 100 | 100 |
| Median check-ins per user | 153 | 173 |
| Maximum check-ins per user | 2,697 | 2,991 |
| `Home (private)` check-ins | 15,382 | 3,106 |

Additional verified facts:

- No malformed rows, blank fields, or invalid coordinate ranges were detected.
- User IDs overlap numerically between the city files because each file uses its own sequence.
- Supplied timezone offsets contain values inconsistent with the city.
- Some venue IDs have conflicting category or coordinate metadata.
- Nearly all users have both weekday and weekend observations.

The notebook must report these checks from code rather than relying only on this specification.

### 4.4 Citation

Cite the dataset's requested reference:

> Yang, D., Zhang, D., Zheng, V. W., & Yu, Z. (2015). Modeling User Activity Preference by Leveraging User Spatial Temporal Characteristics in LBSNs. *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, 45(1), 129–142.

## 5. Data preparation decisions

### 5.1 File format and encoding

Read the source as TSV using `sep="\t"`, `encoding="latin-1"`, explicit column names, and explicit types.

**Rationale:** the text files are already structured tabular data. CSV conversion adds no analytical value and risks changing parsing behavior. UTF-8 fails on the source files.

### 5.2 Duplicate handling

Remove exact duplicate rows and report per-city counts before and after removal.

**Rationale:** repeated identical events would receive extra probability mass and bias entropy.

### 5.3 Time handling

Parse `utc_time` as timezone-aware UTC. Derive local timestamps from the city:

- NYC: `America/New_York`
- Tokyo: `Asia/Tokyo`

Use derived local timestamps for weekday/weekend analysis. Retain the supplied offset for validation, but do not use it as the source of truth.

**Rationale:** NYC requires daylight-saving handling, while the supplied row offsets contain inconsistent values.

### 5.4 Private-home records

Include `Home (private)` check-ins in entropy because they represent routine behavior. Never expose their coordinates, raw users, or individual trajectories in outputs. If time permits, briefly compare results with private-home records excluded.

### 5.5 Conflicting venue metadata

Use each check-in's recorded `category_id` for category entropy. Report the existence of venue/category conflicts, but do not build a canonical venue table.

**Rationale:** canonicalization is unnecessary for venue-ID entropy and exceeds the timebox.

## 6. Metric definitions

### 6.1 Venue entropy

For user `u`, define the probability of observed check-ins at venue `i` as:

\[
p_{u,i}=\frac{n_{u,i}}{N_u}
\]

Calculate Shannon entropy using base-2 logarithms, matching the assignment equation:

\[
H_u=-\sum_i p_{u,i}\log_2(p_{u,i})
\]

Raw entropy is therefore reported in bits.

This measures diversity of observed venue check-ins. It does not measure dwell time, purchases, total mobility, or personality.

### 6.2 Normalized entropy

For `K_u` unique observed locations:

\[
H_{u,\mathrm{norm}}=\frac{H_u}{\log_2(K_u)}
\]

Define normalized entropy as `0.0` when `K_u <= 1`. Its range is `[0, 1]`, subject to floating-point tolerance.

Report raw and normalized entropy together with observation count and unique-location count. Normalization improves comparison but does not eliminate sampling bias.

### 6.3 Category entropy

Apply the same equations using `category_id` as the location variable. Use this as a secondary measure of semantic diversity.

### 6.4 Temporal entropy

Calculate venue entropy independently for weekday and weekend check-ins in local time. Include only users with at least 20 check-ins in each context when comparing the two.

Report excluded-user counts. Use each eligible user's:

\[
\Delta H_{norm}=H_{norm,weekend}-H_{norm,weekday}
\]

## 7. Reusable API

Implement a vectorized pandas function with an interface equivalent to:

```python
calculate_location_entropy(
    data: pd.DataFrame,
    group_cols: str | Sequence[str],
    location_col: str,
    weight_col: str | None = None,
    log_base: float = 2.0,
) -> pd.DataFrame
```

### 7.1 Behavior

- Group by all `group_cols` independently.
- Use row counts when `weight_col=None`.
- Use summed non-negative weights when `weight_col` is provided.
- Allow zero-weight rows but ignore them in the probability distribution.
- Use base 2 by default to match the assignment and support valid configurable bases.
- Use vectorized group operations; do not iterate over users in Python.

### 7.2 Output

Return one row per group with:

- Group columns
- `observation_count`
- `total_weight`
- `unique_location_count`
- `entropy`
- `normalized_entropy`

### 7.3 Validation

- Missing required columns: raise an informative error.
- Null group or location values: raise with counts.
- Non-numeric, negative, or non-finite weights: raise.
- Invalid log base (`<=0` or `==1`): raise.
- Empty input: return an empty DataFrame with the documented output schema.
- Zero total weight for a group: return entropy and normalized entropy as `0.0`, with zero weighted unique locations.

Keep dataset-specific loading and cleaning outside this function.

## 8. Required tests

Create focused unit tests for:

1. One location gives entropy `0`.
2. Uniform visits across `K` locations give entropy `log2(K)` bits and normalized entropy `1`.
3. An unequal hand-calculated distribution matches its expected value.
4. Multiple users and composite groups remain isolated.
5. Weighted entropy works correctly.
6. Configurable log bases work correctly.
7. Missing columns, nulls, invalid weights, and invalid bases fail clearly.
8. Empty input returns the correct empty schema.
9. Zero-weight behavior follows the documented contract.

Use numerical tolerance rather than exact floating-point equality.

## 9. Analysis plan

### 9.1 Core analysis

1. Validate and summarize both datasets.
2. Calculate per-user venue entropy by city.
3. Compare raw and normalized entropy distributions between cities.
4. Examine entropy against check-in count and unique-venue count.
5. Compare weekday and weekend entropy among eligible users.
6. Calculate and compare venue entropy with category entropy.
7. Create within-city behavioral cohorts from normalized venue entropy:
   - Bottom 25%: `routine-oriented`
   - Middle 50%: `mixed`
   - Top 25%: `exploration-oriented`
8. Compare category composition across the low/high cohorts.

Cohort labels are relative descriptions within this dataset, not personality classifications.

### 9.2 Statistical summaries

Prefer robust descriptive statistics:

- Count
- Median
- Interquartile range
- Per-user weekend-minus-weekday difference
- Optional NumPy bootstrap 95% confidence interval for the median difference

Do not center the report on p-values. Large observational samples can make negligible effects appear statistically significant.

### 9.3 Visualizations

Create no more than five focused figures:

1. Normalized venue-entropy distribution by city.
2. Activity/unique-venue count versus entropy.
3. Distribution of weekend-minus-weekday normalized entropy.
4. Venue entropy versus category entropy.
5. Category composition of routine-oriented versus exploration-oriented cohorts.

Do not map individual users, trajectories, or private-home locations. Drop the fifth figure and bootstrap interval first if time is tight.

## 10. How the notebook should read

The notebook is the main report, so it should sound like an analyst walking through real work rather than a list of requirements. Each section should make clear what I was trying to learn, what I found in the data, what choice I made, and what the result means. Important alternatives belong in the narrative when they explain a meaningful tradeoff, not as a mandatory label in every section.

The Markdown should explain the reasoning that code alone cannot show: why the TSV needs Latin-1, why users need city-qualified IDs, why duplicates are removed, how visit shares become probabilities, why entropy is normalized, how local time is derived, why home check-ins remain in the main metric, and why a city comparison has limits. Small worked examples and direct observations from figures are preferable to repeating the code in prose.

## 11. Product narrative and bounded prototype

Develop one primary analytical/product concept: **Context-Aware Discovery**. The notebook must connect computed evidence to a potential user need, product hypothesis, illustrative implementation, and future experiment. It must compare at least three opportunities and keep the historical analysis distinct from product claims.

The companion **Discovery Mode** prototype may implement a transparent deterministic ranker over synthetic profiles and fictional venues. It may adapt venue and category novelty using observation confidence, weekday/weekend context, and an explicit preference. Explicit intent must dominate inferred defaults; sparse histories must shift toward neutral behavior. Entropy remains a ranking signal, never a user-facing personality label.

This permission does not extend to model training, recommendation-quality claims, source-user examples, raw dataset access from the browser, persistence, external venue APIs, or production infrastructure. The prototype demonstrates behavior to evaluate; it is not a trained or validated recommender.

## 12. Privacy and reporting rules

- Present aggregate results only.
- Do not expose raw user IDs.
- Do not display private-home coordinates.
- Do not infer home or work.
- Do not map individual trajectories.
- If user-level examples are necessary, assign generated labels and show non-spatial summaries only.

## 13. Limits that must stay visible

State plainly:

- Check-ins are voluntary and subject to selection and reporting bias.
- Check-ins do not equal dwell time, purchases, demand, or footfall.
- Entropy depends on observation count and observation process.
- Normalization does not remove sampling bias.
- The historical dataset cannot establish current product behavior.
- NYC and Tokyo samples are not representative of their full populations.
- Cross-city differences must not be interpreted as causal or cultural effects.
- Observational findings do not establish causation.

## 14. Project structure

```text
README.md
SPEC.md
PROTOTYPE_SPEC.md
pyproject.toml
uv.lock
apps/web/               # Next.js/React/TypeScript prototype
services/api/           # FastAPI, ranking policy, safe fixtures
scripts/build_demo_profiles.py
src/location_entropy/   # reusable analysis package
tests/                  # analysis and API tests
notebooks/location_entropy_analysis.ipynb
docs/prototype-architecture.svg
dataset_tsmc2014/       # local raw data; ignored by Git
```

Dependencies should remain minimal. Python analysis dependencies are pandas, NumPy, Matplotlib, Seaborn, Jupyter, and pytest; the bounded API adds FastAPI, Pydantic, Uvicorn, and HTTPX for tests. The frontend uses Next.js, React, TypeScript, Vitest, and Testing Library.

Use `uv` for Python dependency management and npm for the frontend. Commit an executed notebook with outputs. The README must include analysis and prototype setup, test commands, dataset sourcing, architecture, disclaimer, screenshot, schema, and citation instructions.

## 15. Production-readiness discussion

Demonstrate production foundations without building production infrastructure:

- Explicit schema and validation
- Reusable metric API
- Separation of loading, calculation, and reporting
- Unit tests
- Deterministic analysis and bootstrap seed
- Relative paths
- Clear errors and documented assumptions

Discuss likely scaling paths only:

- Store validated data as partitioned Parquet.
- Use Polars or Spark for larger data.
- Add pipeline monitoring for schema drift, nulls, duplicates, and distribution changes.
- Version metric definitions and thresholds.

Do not promise hardware-independent runtime. Optionally record observed runtime on the development machine.

## 16. Explicit exclusions

The submission will not include:

- A trained or validated recommender (the synthetic deterministic prototype ranker is permitted)
- Recommendation-effectiveness claims
- Any dashboard/application beyond the single bounded companion prototype
- Authentication, persistence, production deployment infrastructure, or external venue APIs
- Demand forecasting
- Spatial clustering or arbitrary geographic cells
- Individual maps or trajectories
- Causal inference
- A real-time pipeline
- CSV/Parquet conversion
- Extensive hypothesis testing or hyperparameter tuning

## 17. Priorities

The labels below were useful while working within the five-hour timebox. They should not appear as scaffolding in the final notebook.

### P0 — must complete

- Correct loader and validation
- Data-quality report
- Reusable entropy calculation
- Unit tests
- Core two-city analysis
- Methodology, findings, and limitations
- Reproducible notebook and README

### P1 — should complete

- Category entropy
- Weekday/weekend analysis
- Evidence-led primary product proposal

### P2 — complete only if time remains

- Bootstrap confidence intervals
- Fifth visualization
- Sensitivity check excluding `Home (private)`

## 18. Acceptance criteria

The work is complete when:

- [ ] Both Latin-1 TSV files load with explicit schema and expected row counts.
- [ ] Cleaning reports and removes 250 NYC and 577 Tokyo exact duplicates.
- [ ] `(city, user_id)` prevents cross-city user collisions.
- [ ] UTC and derived local timestamps are timezone aware.
- [ ] Entropy API meets its documented contract.
- [ ] Raw and normalized entropy pass hand-calculated tests.
- [ ] All focused tests pass.
- [ ] Both cities are analyzed with the same pipeline.
- [ ] Venue and category entropy are covered.
- [ ] Weekday/weekend analysis applies the 20-per-context threshold and reports exclusions.
- [ ] Figures are readable, labeled, and limited to five.
- [ ] Findings directly answer the main analytical question.
- [ ] Product proposal follows from observed findings and compares at least three opportunities.
- [ ] Notebook distinguishes observations, interpretations, hypotheses, and implementation choices.
- [ ] Notebook includes prototype walkthrough, architecture, evaluation, safeguards, and claim boundary.
- [ ] Reviewer can change synthetic profile, context, and explicit preference in the Next.js frontend and see FastAPI results rerank.
- [ ] Recommendations expose plain-language reasons and score components; sparse history shows neutral fallback.
- [ ] Prototype fixtures contain no source user IDs, coordinates, or trajectories.
- [ ] Backend and frontend critical behavior have automated tests.
- [ ] Privacy, bias, and interpretive limitations are explicit.
- [ ] Notebook explains decisions and rationale section by section and executes without either prototype service running.
- [ ] README documents exact analysis, API, frontend, and test commands.
- [ ] Prototype screenshot and architecture diagram are committed.
- [ ] Raw datasets are excluded from version control and reproducibly sourced.
