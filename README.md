# From Data to Product: Location Entropy + Discovery Mode

**Author:** Jin Tao · **Email:** jintaoyap@gmail.com

This project follows one evidence-led journey:

1. study historical Foursquare check-ins in NYC and Tokyo;
2. measure per-user venue and activity-category diversity;
3. document quality checks, bias, findings, and limitations;
4. compare product opportunities;
5. turn the selected hypothesis into an inspectable Discovery Mode prototype.

The executed [`notebooks/location_entropy_analysis.ipynb`](notebooks/location_entropy_analysis.ipynb) remains the authoritative analysis. The website’s analysis route is generated from that notebook; it is not a second manually maintained report.

> **Claim boundary:** Historical patterns motivate a product hypothesis. They do not show that high-entropy users prefer novel recommendations, that weekends cause exploration, or that entropy-aware ranking improves outcomes. Discovery Mode is a deterministic illustration—not a trained or validated recommender or current place guide.

## Website

The Next.js site has two connected views:

- `/` — generated “From Data to Product” case study with narrative, equations, tables, charts, interpretations, collapsible executed code, artifact fingerprint, and notebook links.
- `/prototype/discovery` — interactive Discovery Mode over synthetic profiles and privacy-safe, data-derived historical candidates.

Static analysis content builds and renders without FastAPI or the raw check-in files. Only the interactive prototype calls the local API.

## Run locally

Requires Python 3.11+, [`uv`](https://docs.astral.sh/uv/), npm, and Node.js `^20.19.0 || >=22.12.0`.

```bash
uv sync --frozen

# Terminal 1: API for Discovery Mode
uv run uvicorn backend.api.main:app --reload

# Terminal 2: website
cd apps/frontend
npm install
npm run dev
```

Open **http://localhost:3000**. The analysis route is immediately available; the prototype requires FastAPI at `http://localhost:8000`.

Set another API base only when needed:

```bash
# apps/frontend/.env.local
NEXT_PUBLIC_DISCOVERY_API_URL=http://localhost:8000
```

Useful API endpoints:

- `GET /health`
- `GET /profiles`
- `GET /venues`
- `POST /recommendations`
- `GET /docs`

Development CORS allows only `http://localhost:3000` and `http://127.0.0.1:3000` by default. Override with comma-separated `DISCOVERY_FRONTEND_ORIGINS`.

## Generated notebook presentation

Export never executes the notebook and never reads raw check-ins. It consumes the already executed notebook, rejects unsafe or unsupported content, converts display tables to structured data, extracts committed images, preserves Markdown and equations, and keeps code in accessible disclosures.

```bash
uv run python scripts/export_notebook_presentation.py \
  --source notebooks/location_entropy_analysis.ipynb \
  --source-label notebooks/location_entropy_analysis.ipynb \
  --artifact apps/frontend/generated/analysis.json \
  --assets apps/frontend/public/generated/analysis
```

Validate freshness and asset fingerprints:

```bash
uv run python scripts/export_notebook_presentation.py \
  --source notebooks/location_entropy_analysis.ipynb \
  --artifact apps/frontend/generated/analysis.json \
  --assets apps/frontend/public/generated/analysis \
  --check
```

`npm run build` runs this freshness check before compiling. The source-controlled notebook presentation metadata records when the web artifact was generated (the exporter falls back to the latest execution completion time for older notebooks); SHA-256 ties the artifact to the exact source notebook bytes.

## Privacy-safe candidate catalog

The candidate catalog is generated offline from actual venue records in the local NYC and Tokyo files:

```bash
uv run python scripts/build_candidate_catalog.py \
  --nyc dataset_tsmc2014/dataset_TSMC2014_NYC.txt \
  --tokyo dataset_tsmc2014/dataset_TSMC2014_TKY.txt \
  --output backend/api/fixtures/venues.json
```

Validate that the committed catalog matches identical local inputs:

```bash
uv run python scripts/build_candidate_catalog.py \
  --nyc dataset_tsmc2014/dataset_TSMC2014_NYC.txt \
  --tokyo dataset_tsmc2014/dataset_TSMC2014_TKY.txt \
  --output backend/api/fixtures/venues.json \
  --check
```

Generation rules:

- exclude `Home (private)` and residential, private, or workplace categories;
- require at least **30 historical check-ins** and **15 distinct visitors**;
- deterministically sample eight eligible candidates per city across the aggregate popularity range;
- round check-in and visitor support to groups of five;
- create honest labels such as `NYC · Coffee Shop · Candidate 08` because source venue names do not exist;
- emit city, source category, rounded support, aggregate popularity percentile, and derived illustrative ranking fields;
- emit no source venue IDs, source user IDs, coordinates, timestamps, or trajectories.

FastAPI loads only this committed safe catalog at startup. It never reads raw check-ins per request, and the browser never receives source records.

### Precise meaning of “new”

“New” means **new to the selected synthetic profile** or **less commonly visited in this 2012–2013 historical sample**. It does not mean newly opened, currently operating, high quality, popular today, or suitable for a real trip.

Profile entropy and candidate novelty are different concepts:

- **Normalized venue/category entropy** describes diversity in an observed synthetic profile history.
- **Aggregate candidate novelty** is the inverse of aggregate historical popularity.
- **Category familiarity** records whether the candidate category appears in the synthetic profile’s familiar history.

No venue receives an entropy score.

## Deterministic ranking policy

Explicit choices map to discovery levels `0.20`, `0.50`, and `0.80`. Explicit intent contributes 70% of applied discovery; confidence-adjusted profile diversity contributes 30%; a reliable weekend difference can add a modest weekend-only adjustment. Sparse profiles regress the inferred part toward neutral (`0.50`).

Baseline relevance is an explicitly illustrative transform of aggregate historical popularity. Aggregate candidate novelty is its inverse. Category familiarity remains separate. A bounded weighting curve keeps familiar mode relevance-led while allowing “Show me something new” to visibly rerank the same pool. Generated candidate ID breaks ties.

These equations encode an inspectable product hypothesis, not learned relevance or recommendation effectiveness.

## Tests and builds

```bash
# Python analysis, exporter, generator, ranking, and API
uv run pytest

# Frontend tests, route types, TypeScript, and production build
cd apps/frontend
npm test
npm run typecheck
npm run build
```

The test seams are the generated artifact contract, candidate-catalog output, FastAPI contract, and rendered analysis/prototype experience.

## Dataset

The recommended EPFL mobility data were unavailable, so this analysis uses the **Foursquare TSMC 2014 NYC and Tokyo Check-in Dataset**.

Download from the [dataset author’s page](https://sites.google.com/site/yangdingqi/home/foursquare-dataset), extract locally, and preserve the raw headerless Latin-1 TSV files unchanged:

```text
dataset_tsmc2014/
  dataset_TSMC2014_NYC.txt
  dataset_TSMC2014_TKY.txt
  dataset_TSMC2014_readme.txt
```

`dataset_tsmc2014/` is ignored by Git.

| File | Rows | SHA-256 |
|---|---:|---|
| `dataset_TSMC2014_NYC.txt` | 227,428 | `2f39ce698e5bff6683c74bec30c436cc022c160b0f3d73c5268b55491b2445f9` |
| `dataset_TSMC2014_TKY.txt` | 573,703 | `85542c605ce708d8584637756590383a84e9bbdb71342d0d8e78858ba2a0e5c8` |

The loader applies explicit fields for user, venue, category, coordinates, supplied offset, and UTC time. It derives authoritative local time by city. Users are keyed by `(city, user_id)` because IDs restart between files.

## Project layout

```text
apps/frontend/app/                     # Next.js analysis and prototype routes
apps/frontend/components/              # generated-story and Discovery Mode renderers
apps/frontend/generated/analysis.json  # committed notebook presentation artifact
apps/frontend/public/generated/        # committed chart/reference assets
backend/api/                            # FastAPI schemas and deterministic ranker
backend/api/fixtures/venues.json        # safe aggregate candidate catalog
scripts/export_notebook_presentation.py
scripts/build_candidate_catalog.py
scripts/build_demo_profiles.py
src/location_entropy/                  # reusable loading and metric package
notebooks/location_entropy_analysis.ipynb
tests/                                  # analysis, artifact, catalog, and API tests
```

## Metric API

```python
calculate_location_entropy(data, group_cols, location_col)
```

The vectorized function returns event count, unique-location count, base-2 entropy in bits, and normalized entropy for each group. It supports composite keys and validates missing columns and null grouping fields.

## Citation

Yang, D., Zhang, D., Zheng, V. W., & Yu, Z. (2015). Modeling User Activity Preference by Leveraging User Spatial Temporal Characteristics in LBSNs. *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, 45(1), 129–142.
