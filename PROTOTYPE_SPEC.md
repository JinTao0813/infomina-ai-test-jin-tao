# Context-Aware Discovery — Analysis and Prototype Specification

## 1. Purpose

Extend the location-entropy submission from a correct analysis into a clear product argument and a small, clickable full-stack demonstration.

The work must show this chain explicitly:

> observed evidence → cautious interpretation → user need → product hypothesis → interactive behavior → evaluation plan

The notebook remains the authoritative analysis. The prototype demonstrates one possible use of the findings; it is not a trained recommender or evidence that entropy-based personalization improves outcomes.

## 2. Audience and success criteria

Primary audience: interview reviewers assessing data-science reasoning, product judgment, and engineering range.

A reviewer should be able to:

1. Understand the principal findings without reading every code cell.
2. See how each proposed product idea follows from a specific finding.
3. Distinguish observed evidence from hypotheses and implementation choices.
4. Run a Next.js/React frontend and Python API locally.
5. change a demo profile, context, and discovery preference;
6. See recommendations rerank and understand why.
7. See appropriate privacy, uncertainty, and evaluation safeguards.

## 3. Settled product terminology

- **Analytical/product concept:** Context-Aware Discovery
- **Prototype feature:** Discovery Mode
- **User prompt:** “What feels right today?”
- **Choices:** Keep it familiar / Balanced / Show me something new

Do not use “Adaptive Discovery Dial.” Do not expose entropy as a personality label.

## 4. Evidence available from the analysis

The product discussion may rely on these executed-notebook findings:

| Finding | Evidence | Defensible interpretation |
|---|---|---|
| City medians are similar | Median normalized venue entropy: NYC 0.853, Tokyo 0.860 | Within-city user variation is more useful for personalization than city-level stereotypes. |
| Weekend diversity is often higher | Positive weekend-minus-weekday difference for 88.5% of eligible NYC users and 85.4% of eligible Tokyo users; medians 0.058 and 0.059 | Recommendation novelty may be context-dependent for sufficiently observed users. |
| Place and activity diversity differ | Venue/category entropy rank correlation: NYC 0.897, Tokyo 0.728; median category entropy 0.810 and 0.707 | Venue novelty and category novelty should be treated as separate controls. |
| Metrics depend on observed history | Entropy remains related to check-in and unique-venue counts | Inferred behavior needs observation thresholds and confidence-aware fallback. |

Required claim boundary:

> These patterns motivate product hypotheses. They do not show that high-entropy users prefer novel recommendations, that weekends cause exploration, or that entropy-aware ranking improves engagement.

## 5. Notebook modification plan

Target: `notebooks/location_entropy_analysis.ipynb`

### 5.1 Preserve

Keep the following analytical sections and calculations materially unchanged:

- dataset loading and quality checks;
- entropy definitions and worked example;
- city comparison;
- observation-bias discussion;
- weekday/weekend analysis;
- venue/category comparison;
- limitations, privacy rules, and aggregate reporting.

Do not add model training, causal claims, individual trajectories, maps, or raw user examples.

### 5.2 Revise the executive summary

Replace the final sentence of the current summary with a compact evidence-to-product conclusion:

> The analysis identifies three potentially actionable patterns: differences between users are more substantial than the small difference between city medians; most sufficiently observed users show higher weekend venue entropy; and venue diversity does not always imply activity-category diversity. These findings motivate Context-Aware Discovery, demonstrated through a companion full-stack prototype. The prototype is a testable product hypothesis, not a validated recommender.

### 5.3 Rename and narrow section 7

Rename:

> `## 7. Category entropy and product implication`

To:

> `## 7. Venue diversity and activity diversity`

Keep this section analytical. Remove the current product-proposal paragraph from it. End with the implication that venue and category novelty are distinct ranking dimensions, while explicitly avoiding preference claims.

### 5.4 Add section 8: Insights and product opportunities

Add an evidence-to-opportunity table:

| Finding | Potential user or business need | Product opportunity |
|---|---|---|
| User variation exceeds the city-median difference | Personalization without geographic stereotyping | Context-Aware Discovery |
| Weekend entropy is higher for most eligible users | Recommendations that reflect changing context | Weekend discovery adjustment |
| Venue and category diversity differ | Choose between a new place and a new kind of activity | Separate venue/category novelty controls |
| Sparse histories are less reliable | Avoid premature personalization | Confidence-aware cold start |
| Concentrated histories may be sensitive | Transparency and control over inferred behavior | Privacy/predictability summary |

Briefly compare four concepts:

1. **Context-Aware Discovery** — selected primary concept; strongest connection to all principal findings.
2. **Weekend Discovery Mode** — useful as part of the primary concept, not a standalone product.
3. **Merchant Audience Insights** — plausible aggregate extension, but check-ins are not footfall or purchases.
4. **Privacy and Predictability Summary** — useful extension, but entropy alone is not a privacy-risk score.

### 5.5 Add section 9: Selected concept and product hypothesis

State:

> People may receive more useful venue suggestions when venue novelty and activity-category novelty are adjusted using observed behavioral diversity, reliable temporal context, and an explicit user preference.

Describe product behavior:

- concentrated venue history → favor new venues within familiar activities;
- broad venue but narrower category history → selectively introduce a new activity category;
- broad venue and category history → permit wider discovery;
- reliable positive weekend difference → modestly raise weekend novelty;
- sparse history → use a neutral fallback and rely more on explicit preference;
- explicit preference always dominates the inferred default.

State that entropy is a ranking signal, not a user-facing identity.

### 5.6 Add section 10: Prototype walkthrough and architecture

Include:

- one committed screenshot of the selected interface;
- a small architecture diagram;
- one example API request/response;
- ranking-policy summary;
- local run commands or a link to the README;
- clear disclaimer that demo profiles and venues are synthetic.

Suggested architecture:

```text
Browser
  ↓
Next.js + React + TypeScript
  ↓ JSON/HTTP
FastAPI + Pydantic
  ↓
Deterministic ranking policy + synthetic demo fixtures
  ↓
Reusable entropy concepts from src/location_entropy
```

The notebook must render without either service running. Commit static screenshot/diagram assets rather than embedding a live application.

### 5.7 Add section 11: Evaluation and safeguards

Define a future randomized experiment:

- **Control:** baseline relevance ranking.
- **Treatment:** context-aware ranking with the same candidate pool and explicit override.
- **Primary metric:** save or selection rate per recommendation impression.
- **Secondary metrics:** category discovery rate, catalog coverage, and return engagement.
- **Guardrails:** hides/dismissals, early exits, repeated suggestions, travel distance, latency, and sparse-history performance.
- **Segments:** baseline entropy, confidence, context, city, and explicit discovery choice.

Ask the correct validation question:

> Does adapting recommendation novelty with these signals improve user outcomes relative to the baseline ranker?

Do not imply that offline entropy correlations answer this question.

### 5.8 Revise conclusion

Conclude with three layers:

1. what the historical data show;
2. which hypothesis follows;
3. what evidence is still required.

Keep existing limits around voluntary check-ins, selection bias, historical relevance, city representativeness, metadata conflicts, and private-home records.

## 6. Prototype scope

### 6.1 Deliverable

A responsive single-page full-stack prototype in which a reviewer can:

1. Select an anonymous demo profile.
2. Switch between weekday and weekend.
3. Choose Familiar, Balanced, or Something new.
4. Request recommendations.
5. See the result cards rerank.
6. Inspect a plain-language reason and score breakdown for each result.
7. See the profile signals and confidence used by the system.

This is a functional interaction prototype with a real Python API, not a static mockup.

### 6.2 Explicit non-goals

- Authentication or accounts
- Database or persistence
- Maps, geocoding, or live location
- External venue/recommendation APIs
- Model training or collaborative filtering
- Production deployment infrastructure
- Real-time ingestion
- Raw dataset access from the browser
- Individual historical users or trajectories
- Claims of recommendation quality

## 7. Technical architecture

```text
apps/web/                         # Next.js, React, TypeScript
  app/
  components/
  lib/
  public/prototype/

services/api/                     # FastAPI
  main.py
  ranking.py
  schemas.py
  fixtures/
    profiles.json
    venues.json

src/location_entropy/            # existing reusable Python analysis package
scripts/
  build_demo_profiles.py         # deterministic aggregate-to-synthetic artifact build
notebooks/
  location_entropy_analysis.ipynb
```

### 7.1 Frontend

- Next.js App Router
- React and TypeScript
- One route: `/prototype/discovery`
- Client-side controls and result updates
- Environment-configured API base URL
- No frontend access to raw check-in files

### 7.2 Backend

- FastAPI and Pydantic
- Deterministic in-memory fixtures loaded at startup
- Existing entropy package imported where metric behavior is needed
- CORS restricted to documented local frontend origins in development
- No persistence

### 7.3 Offline/online boundary

`build_demo_profiles.py` may read aggregate notebook outputs or recalculate aggregate ranges using the existing entropy module. It must output synthetic profiles without source user IDs, coordinates, or trajectories.

The API loads only safe fixtures. It must not load the 800,000-row source dataset per request or return source records.

## 8. Demo data contract

### 8.1 Profiles

Provide four synthetic profiles:

| Profile | Purpose |
|---|---|
| Routine-oriented | Concentrated history with high confidence |
| Mixed | Values near the observed medians |
| Exploration-oriented | Broad venue and category history |
| New/sparse history | Low confidence and neutral inferred default |

Each profile contains:

```json
{
  "id": "routine",
  "label": "Routine-oriented demo",
  "venue_entropy": 0.72,
  "category_entropy": 0.58,
  "weekend_delta": 0.04,
  "observation_count": 180,
  "confidence": 0.90,
  "familiar_categories": ["Coffee Shop", "Park"]
}
```

Values are synthetic but should be anchored to observed aggregate ranges. The UI must label them as demo data.

### 8.2 Candidate venues

Provide 12–20 fictional candidates with:

- stable ID;
- fictional name;
- category;
- short description;
- baseline relevance in `[0,1]`;
- venue novelty in `[0,1]`;
- category novelty in `[0,1]`;
- normalized distance penalty in `[0,1]`;
- optional local image/icon asset.

Do not reuse source venue IDs, coordinates, or private-home categories.

## 9. Ranking policy

The policy must be transparent, deterministic, and documented as illustrative.

### 9.1 Applied discovery level

Map explicit choices to values:

- Familiar: `0.20`
- Balanced: `0.50`
- Something new: `0.80`

Calculate:

```text
inferred_discovery = 0.60 × venue_entropy + 0.40 × category_entropy
confidence_adjusted = confidence × inferred_discovery + (1 − confidence) × 0.50
context_adjustment = confidence × weekend_delta when context is weekend, otherwise 0
applied_discovery = clamp(
  0.70 × explicit_choice
  + 0.30 × confidence_adjusted
  + context_adjustment,
  0,
  1
)
```

This makes explicit intent dominant and causes sparse profiles to fall toward neutral behavior.

### 9.2 Candidate score

```text
novelty_score = 0.60 × venue_novelty + 0.40 × category_novelty
final_score =
  (1 − applied_discovery) × baseline_relevance
  + applied_discovery × novelty_score
  − 0.15 × distance_penalty
```

Return components so the UI can explain the result. Stable candidate ID breaks ties.

### 9.3 Explanation rules

Generate deterministic reasons from dominant score components, for example:

- “A new venue in a familiar activity category.”
- “A broader activity choice for your weekend setting.”
- “Prioritized for relevance because you chose to keep it familiar.”
- “Using a neutral starting point because this demo profile has limited history.”

Never say the system knows a user’s personality, home, work, or intent.

## 10. API contract

### `GET /health`

Returns service status.

### `GET /profiles`

Returns safe synthetic profile summaries.

### `GET /venues`

Returns fictional candidate metadata for debugging/demo transparency.

### `POST /recommendations`

Request:

```json
{
  "profile_id": "routine",
  "context": "weekend",
  "discovery_mode": "balanced",
  "limit": 6
}
```

Response:

```json
{
  "profile": {
    "id": "routine",
    "venue_entropy": 0.72,
    "category_entropy": 0.58,
    "confidence": 0.90
  },
  "context": "weekend",
  "applied_discovery": 0.48,
  "recommendations": [
    {
      "id": "venue-07",
      "name": "Riverside Coffee Lab",
      "category": "Coffee Shop",
      "final_score": 0.82,
      "baseline_relevance": 0.88,
      "venue_novelty": 0.73,
      "category_novelty": 0.14,
      "reason": "A new venue in a familiar activity category."
    }
  ],
  "disclaimer": "Illustrative ranking over fictional venues; not a validated recommender."
}
```

Validation:

- unknown profile → `404`;
- invalid enum or limit → `422`;
- limit constrained to `1–12`;
- no raw identifiers or coordinates in responses.

## 11. UX specification

### 11.1 Visitor mode

Operate/read hybrid: the reviewer changes controls to understand system behavior, then reads why the ranking changed.

### 11.2 Information hierarchy

1. Title and one-sentence product hypothesis
2. Demo-data disclaimer
3. Profile selector
4. “What feels right today?” choice
5. Weekday/weekend context
6. Applied-discovery summary
7. Ranked recommendation results
8. Expandable “Why this ranking?” details
9. Methodology, privacy, and experiment notes

### 11.3 Required states

- Initial/default state: Mixed + Weekday + Balanced
- Loading
- Successful rerank
- API unavailable/error with retry
- Empty result state
- Sparse-profile explanation
- Narrow mobile layout

### 11.4 Interaction requirements

- Controls are keyboard accessible and visibly focused.
- Changing a control reruns ranking immediately or through one clearly labeled action; select one behavior and use it consistently.
- Reranking should preserve focus and announce result updates with an appropriate live region.
- Score details are available but secondary to plain-language explanations.
- Do not use color alone to distinguish familiarity and novelty.
- Respect reduced-motion preferences.
- Meet WCAG AA contrast targets.

### 11.5 Responsive behavior

- Desktop: controls beside or above a multi-column result area.
- Mobile: controls stack before a single-column list.
- No critical information appears only on hover.
- Test at approximately 375px and 1440px widths.

### 11.6 Visual exploration checkpoint

Before selecting the final screen, create three structurally different variants on the same prototype route, switchable by `?variant=`:

- **A — Recommendation-first:** controls followed by prominent result cards.
- **B — Explain-first:** profile and applied-discovery explanation beside results.
- **C — Comparison:** familiar and exploratory outcomes shown side by side.

Select one based on clarity of cause-and-effect, mobile viability, and screenshot quality. Promote only the winner into the final prototype; archive/remove the switcher and losing variants from the submission branch.

## 12. Testing and quality

### 12.1 Existing analysis

All existing tests must continue to pass.

### 12.2 Python API tests

Test:

- discovery-level calculation;
- explicit choice dominance;
- weekend adjustment only in weekend context;
- sparse-history neutral fallback;
- deterministic ordering and tie-breaking;
- request validation;
- unknown profiles;
- response contains no forbidden raw fields.

### 12.3 Frontend tests

At minimum verify:

- initial state renders;
- selecting profile/context/mode sends the expected request;
- returned order and explanation render;
- loading and API-error states;
- keyboard-operable controls.

### 12.4 Manual acceptance flow

1. Open the prototype at desktop width.
2. Record the default recommendation order.
3. Switch Familiar → Something new and confirm visible reranking.
4. Switch Weekday → Weekend and confirm applied-discovery value changes for a reliable profile.
5. Select sparse profile and confirm neutral-fallback explanation.
6. Expand one score explanation.
7. Repeat the core flow at mobile width and by keyboard.

## 13. Documentation changes outside the notebook

### `README.md`

Add:

- prototype purpose and disclaimer;
- architecture summary;
- API and frontend setup;
- exact run commands;
- demo URL;
- test commands;
- screenshot;
- statement that fixtures are synthetic and the source check-ins remain local.

Expected commands:

```bash
# Existing analysis
uv sync --frozen
uv run pytest
uv run jupyter lab notebooks/location_entropy_analysis.ipynb

# Python API
uv run uvicorn services.api.main:app --reload

# Next.js frontend
cd apps/web
npm install
npm run dev
```

### `SPEC.md`

Resolve current contradictions:

- Replace “Do not implement a recommender” with a distinction between a deterministic prototype ranker and a trained/validated recommender.
- Remove “dashboard or application” from absolute exclusions; permit the bounded companion prototype.
- Keep model training, production infrastructure, persistence, and effectiveness claims excluded.
- Add the notebook product sections and prototype acceptance criteria.

### New supporting assets

```text
docs/prototype-architecture.svg
apps/web/public/prototype/discovery-mode.png
```

## 14. Implementation phases

### Phase 1 — Analysis narrative

- Revise notebook headings and product narrative.
- Add opportunity comparison, selected hypothesis, evaluation, and claim boundaries.
- Update `SPEC.md` so scope is internally consistent.

### Phase 2 — Safe demo artifacts and API

- Add FastAPI/Pydantic dependencies.
- Create synthetic profiles and fictional venues.
- Implement deterministic ranking and API endpoints.
- Add backend tests.

### Phase 3 — Clickable frontend

- Scaffold Next.js/React/TypeScript app.
- Build three temporary layout variants.
- Select and retain one direction.
- Connect frontend to FastAPI.
- Implement loading, error, sparse-history, responsive, and accessible states.

### Phase 4 — Integration and handoff

- Capture screenshot and architecture asset.
- Add static prototype walkthrough to notebook.
- Update README run/test instructions.
- Execute notebook end to end.
- Run Python and frontend tests.
- Perform desktop/mobile manual acceptance flow.

## 15. Acceptance criteria

### Analysis documentation

- [ ] Every product claim links to a computed result.
- [ ] Observations, interpretations, hypotheses, and implementation choices are clearly distinguished.
- [ ] At least three product opportunities are compared.
- [ ] Context-Aware Discovery is justified as the selected concept.
- [ ] Prototype limitations and future experiment are explicit.
- [ ] Existing analytical/privacy limitations remain visible.
- [ ] Notebook renders fully without running the prototype services.

### Prototype

- [ ] Next.js/React/TypeScript frontend runs locally.
- [ ] FastAPI backend runs locally and exposes documented endpoints.
- [ ] Reviewer can change profile, context, and discovery mode.
- [ ] At least two control changes visibly alter ranking.
- [ ] Every recommendation has a plain-language explanation.
- [ ] Sparse history triggers neutral fallback behavior.
- [ ] Inputs and output are synthetic and contain no source user IDs or coordinates.
- [ ] No database, authentication, map, external API, or trained model is introduced.
- [ ] Core interactions work by keyboard and at mobile width.
- [ ] Automated tests cover ranking behavior and critical UI states.

### Repository

- [ ] Existing tests still pass.
- [ ] Notebook executes end to end.
- [ ] README contains exact setup/run/test instructions.
- [ ] `SPEC.md` no longer contradicts the prototype scope.
- [ ] Prototype screenshot and architecture diagram are committed.

## 16. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Prototype overshadows analysis | Keep notebook authoritative; limit prototype to one page and one ranking policy. |
| Demo appears to claim recommendation quality | Use persistent disclaimer and explicit experiment plan. |
| Historical users are re-identifiable | Use synthetic profiles and fictional venues only. |
| Entropy becomes a personality label | Describe observed behavior and confidence; never identity or intent. |
| Full-stack work expands beyond interview value | No auth, database, maps, external APIs, training, or deployment infrastructure. |
| Frontend and Python duplicate business logic | Ranking lives in Python; frontend renders API results. |
| Sparse histories produce false precision | Confidence-adjust toward neutral and explain the fallback. |

## 17. Open decisions before implementation

1. Final visual direction: choose A, B, or C after the three-variant checkpoint.
2. Whether control changes rerank immediately or require an “Update recommendations” action.
3. Whether to include small locally stored illustration assets or use typography/icons only.
4. Whether to deploy the prototype; local execution is sufficient for this specification.

All other scope and behavior above are considered settled unless implementation exposes a material issue.
