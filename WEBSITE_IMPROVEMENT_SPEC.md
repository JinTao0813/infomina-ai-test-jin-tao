## Problem Statement

The current submission separates the authoritative analysis notebook from the Discovery Mode prototype. A reviewer who lands on the website sees the prototype before seeing the evidence, analytical decisions, findings, product-opportunity comparison, or the reasoning that connects entropy to ranking behavior. This makes the prototype feel unexplained and can imply that entropy is a score attached to places or that the analysis already proves recommendation quality.

The current prototype also ranks wholly fictional venues with hand-authored candidate scores. That protects source data, but weakens the visible connection to the Foursquare dataset. The source dataset can support a more relevant demonstration, but it contains no venue names and its historical venue records must not be presented as current recommendations. User entropy is calculated from a user's observed check-in distribution; it is not a venue-level quality score. Candidate novelty must therefore remain a distinct, explicitly defined ranking input.

Reviewers need one coherent website journey that shows the complete path from studying the data through analysis, findings, product ideas, selected hypothesis, and prototype, while retaining the executed notebook as the reproducible technical source of truth.

## Solution

Create a responsive “From Data to Product” website experience with two connected views:

1. An analysis case study that presents the complete executed-notebook narrative: objective, dataset, quality checks, preparation, entropy methodology, city comparison, observation bias, weekday/weekend analysis, venue/category analysis, findings, opportunity comparison, selected product hypothesis, evaluation plan, limitations, and conclusion.
2. An improved Discovery Mode prototype that begins with a concise evidence-to-product explanation and ranks privacy-safe, data-derived venue candidates rather than arbitrary fictional candidates.

The executed notebook remains authoritative and downloadable. A deterministic export step converts the executed notebook into a committed, website-safe presentation artifact, so the web documentation is generated rather than maintained as an independent analysis. Code is retained in collapsible sections, while findings, charts, and interpretation remain prominent.

The candidate catalog is generated offline from actual venue records in the analysed dataset. Because the dataset has no venue names, the interface uses transparent pseudonymous labels such as city, category, and a generated candidate number; it does not invent names and imply they are real. The generated catalog excludes private-home and sensitive categories, source venue IDs, exact coordinates, source user IDs, and trajectories. It may include safe aggregate fields such as city, category, total check-ins, distinct visitor count, and an aggregate popularity percentile when minimum-support thresholds are met.

The product explanation must state that:

- normalized venue and category entropy describe diversity in an observed user history;
- entropy is a profile-level personalization signal, not a score for venue quality or freshness;
- candidate novelty is a separate, transparent signal derived from aggregate historical popularity and whether a category is familiar to the selected synthetic profile;
- “new” means new to the user or less commonly visited in this historical sample, not newly opened;
- the deterministic ranker is an illustrative discovery-ranking hypothesis, not a trained or validated recommender.

## User Stories

1. As an interview reviewer, I want a clear landing page, so that I immediately understand the project’s question and end-to-end story.
2. As an interview reviewer, I want to move through the work in analytical order, so that I can follow how the product idea emerged.
3. As an interview reviewer, I want a concise executive summary, so that I can understand the principal findings before reading details.
4. As an interview reviewer, I want to see the dataset source, scope, cities, row counts, and citation, so that I can assess provenance.
5. As an interview reviewer, I want to see data-quality checks and preparation decisions, so that I can judge whether the metric is trustworthy.
6. As an interview reviewer, I want duplicate, timezone, identifier, metadata-conflict, and private-home handling explained, so that important caveats are not hidden.
7. As an interview reviewer, I want a plain-language definition of location entropy, so that I can understand what it measures.
8. As a technical reviewer, I want equations and the worked entropy example retained, so that I can verify the methodology.
9. As a technical reviewer, I want notebook code available in collapsible sections, so that reproducibility is preserved without overwhelming the narrative.
10. As an interview reviewer, I want charts and computed summaries displayed beside their interpretations, so that claims remain tied to evidence.
11. As an interview reviewer, I want the NYC and Tokyo comparison explained cautiously, so that small differences are not presented as stereotypes or causal effects.
12. As an interview reviewer, I want observation-count bias explained, so that normalized entropy is not treated as bias-free.
13. As an interview reviewer, I want the weekday/weekend analysis and eligibility threshold explained, so that I understand the context signal’s limits.
14. As an interview reviewer, I want venue and category entropy distinguished, so that place diversity is not confused with activity diversity.
15. As an interview reviewer, I want observations, interpretations, hypotheses, and implementation choices visually distinguished, so that evidence strength is clear.
16. As a product reviewer, I want multiple product opportunities compared, so that the selected concept does not appear arbitrary.
17. As a product reviewer, I want the selected Context-Aware Discovery hypothesis stated explicitly, so that I know what the prototype is testing.
18. As a product reviewer, I want an evidence-to-product bridge before the prototype, so that I understand why entropy appears in the ranking policy.
19. As a product reviewer, I want to know that entropy describes user history rather than venues, so that I do not misread candidate scores.
20. As a product reviewer, I want “new” and “fresh” defined precisely, so that historical novelty is not mistaken for a recently opened venue.
21. As a reviewer, I want direct navigation between analysis and prototype, so that the two artifacts feel like one case study.
22. As a reviewer, I want a visible progress or section navigation aid, so that I can scan a long analysis page efficiently.
23. As a reviewer, I want to open or download the original notebook, so that I can inspect the authoritative executable report.
24. As a reviewer, I want the website documentation generated from the executed notebook, so that the notebook and website do not silently drift.
25. As a reviewer, I want to see when the web artifact was generated and which notebook it came from, so that freshness is inspectable.
26. As a reviewer, I want static analysis content to render without the FastAPI service or raw dataset, so that documentation remains accessible independently.
27. As a prototype user, I want actual dataset-derived candidate records, so that the demonstration has a visible connection to the analysis.
28. As a prototype user, I want candidate labels to be honest about the absence of source venue names, so that generated names are not misrepresented as real venues.
29. As a privacy-conscious reviewer, I want source venue IDs, user IDs, exact coordinates, private-home categories, and trajectories excluded, so that the demo does not expose sensitive records.
30. As a prototype user, I want each candidate’s city, category, and safe aggregate provenance shown, so that I can understand what is data-derived.
31. As a prototype user, I want to know that the venue sample is historical, so that I do not interpret it as a current place guide.
32. As a prototype user, I want to select a synthetic profile, weekday/weekend context, and explicit discovery preference, so that I can inspect ranking behavior.
33. As a prototype user, I want explicit preference to remain the strongest input, so that inferred history does not override stated intent.
34. As a prototype user, I want sparse histories to use a neutral fallback, so that the system does not display false precision.
35. As a prototype user, I want recommendation order to visibly change when discovery preference changes, so that cause and effect is demonstrable.
36. As a prototype user, I want a short “why recommended” statement on every candidate, so that rankings are understandable without opening technical details.
37. As a technical reviewer, I want an expandable score breakdown, so that I can inspect relevance, aggregate novelty, category familiarity, context, and final score.
38. As a technical reviewer, I want candidate novelty and profile entropy labeled separately, so that independent concepts are not conflated.
39. As a technical reviewer, I want the candidate-generation rules documented, so that “data-derived” is reproducible rather than a marketing claim.
40. As a reviewer, I want a persistent claim boundary, so that the prototype is not mistaken for a trained or validated recommender.
41. As a reviewer, I want the future randomized evaluation described, so that I know what evidence would validate the product hypothesis.
42. As a reviewer, I want privacy, bias, historical relevance, and representativeness limitations kept visible, so that the product narrative remains responsible.
43. As a keyboard user, I want all navigation, controls, disclosures, and prototype interactions operable without a pointer, so that the complete story is accessible.
44. As a screen-reader user, I want semantic headings, landmarks, descriptive links, table captions, chart alternatives, and live reranking announcements, so that the experience is understandable.
45. As a mobile reviewer, I want the analysis and prototype to remain readable at narrow widths, so that no essential content requires horizontal scrolling or hover.
46. As a motion-sensitive user, I want reduced-motion preferences respected, so that navigation and reranking remain comfortable.
47. As a developer, I want export and candidate generation to be deterministic, so that identical inputs produce reviewable artifacts.
48. As a developer, I want generated artifacts validated before commit or build, so that stale, unsafe, or malformed content fails clearly.
49. As a developer, I want the frontend build to avoid reading the raw 800,000-row dataset, so that deployment remains bounded and reproducible.
50. As a developer, I want the existing notebook and API behavior preserved unless explicitly superseded here, so that the improvement does not regress completed analysis work.

## Implementation Decisions

- The website information architecture will use a data-to-product case study as the primary entry point and Discovery Mode as a connected prototype view. Shared navigation, terminology, visual tokens, and claim boundaries will make them one experience.
- The case-study order will follow the executed notebook: objective and summary; dataset and quality; preparation; methodology; core findings; observation bias; temporal findings; venue/category findings; product opportunities; selected hypothesis; prototype; evaluation; limitations and conclusion.
- The executed notebook remains the canonical analytical artifact. The website will not become a second manually maintained source of computed facts.
- A deterministic notebook-presentation exporter will consume the already executed notebook and produce a committed, website-safe artifact. It will not execute the notebook or require raw data during the frontend build.
- The generated artifact will preserve narrative Markdown, equations, tables, aggregate outputs, and charts. Code cells will be available through accessible disclosures and de-emphasized by default. Empty/debug cells and nonessential execution noise may be omitted without removing analytical decisions or results.
- The artifact will include generation metadata and a content fingerprint tied to the source notebook. A validation command will detect when the committed web artifact no longer matches the notebook.
- The website renderer will use the trusted generated artifact rather than accepting arbitrary user-authored HTML. The export step will reject unexpected active content, scripts, external embeds, or unsafe output types.
- Charts will include captions and concise text alternatives describing the analytical takeaway, not only visual appearance.
- The analysis view will provide anchored section navigation and clear links to the original notebook and the interactive prototype.
- The prototype will begin with a compact three-step bridge: what the analysis measured, how profile-level entropy becomes one ranking signal, and what the prototype does not prove.
- Product copy will prefer “discovery ranking,” “less commonly visited in the historical sample,” and “new to the user.” It will not call a candidate newly opened without opening-date data.
- Entropy will remain attached to synthetic profiles. No venue will be displayed as having a “location entropy score.”
- Candidate novelty will be renamed and defined as a separate aggregate candidate signal. It will not be presented as recommendation quality.
- The arbitrary fictional venue fixture will be replaced by a deterministic, privacy-safe candidate catalog generated offline from actual venue records in the analysed NYC and Tokyo files.
- Because the source dataset does not contain venue names, generated candidate labels will be explicitly pseudonymous and descriptive. The system will not invent plausible proper names and present them as source data.
- Candidate generation will exclude `Home (private)` and other sensitive or residential categories, require a documented minimum number of check-ins and distinct visitors, and remove source venue IDs, source user IDs, exact coordinates, timestamps, and trajectories.
- Safe candidate fields may include generated candidate ID, city, source category name, total historical check-ins, distinct historical visitors, aggregate popularity percentile, and a generated descriptive label. The API and browser receive only the safe generated catalog.
- Aggregate values will be rounded or bucketed where needed to avoid exposing rare records. Selection thresholds and tie-breaking will be deterministic and documented.
- The API will load the committed safe catalog at startup. It will never load raw check-ins per request and the frontend will never access raw data.
- Baseline relevance will be an explicitly illustrative score derived from a documented aggregate popularity transform. Candidate novelty will be derived from the inverse of that aggregate popularity measure. Profile-specific category familiarity will remain a separate adjustment.
- Distance will be removed from the core ranking explanation unless a defensible, privacy-safe, and clearly labeled synthetic location input is retained. The first implementation should optimize for a minimal explanation centered on evidence from this analysis rather than unrelated scoring factors.
- The existing deterministic policy remains bounded: explicit discovery choice dominates, reliable weekend context provides only a modest adjustment, and sparse profiles regress inferred behavior toward neutral.
- Recommendation responses will expose the components needed to explain the result and the provenance label needed to distinguish dataset-derived fields from illustrative ranking fields.
- The prototype will continue to use synthetic profiles. It will not select or display real source users, even when candidates are derived from real venue records.
- The interface will show a persistent note that the source check-ins are historical and cannot establish whether a venue still exists or is currently desirable.
- Existing loading, error, empty, sparse-history, responsive, keyboard, visible-focus, live-region, and reduced-motion behavior will be retained or improved.
- Documentation and prototype pages will share accessible header/navigation patterns and remain usable around 375px and 1440px widths.
- The README will explain the data-to-product website, notebook export, candidate-catalog generation, local run steps, validation commands, privacy boundary, and precise meaning of “new.”

## Testing Decisions

- Tests will assert externally visible behavior and artifact contracts, not React component structure, CSS implementation, exporter helper functions, or ranking internals.
- The primary/highest seam will be the rendered website experience: one route-level frontend test will verify that a reviewer can navigate the generated analysis story, encounter the evidence-to-product bridge, enter Discovery Mode, change controls, and see an explained rerank using a mocked API response. This extends the existing React Testing Library precedent and keeps the main behavior test at one user-facing seam.
- Analysis rendering tests will verify required section headings, notebook/download link, generation metadata, collapsible code access, chart alternatives, and the claim boundary from a representative generated artifact.
- Export-contract tests will run the exporter against a small fixture notebook and assert deterministic output, preserved Markdown/equations/tables/images, omission of active content, and a clear failure for unsupported unsafe outputs. They will not snapshot an entire HTML document.
- Freshness validation will prove that changing the source notebook fingerprint causes the generated-artifact check to fail and re-export causes it to pass.
- Candidate-catalog tests will exercise the offline generator at its output seam. They will assert deterministic selection, minimum-support enforcement, sensitive-category exclusion, pseudonymous labels, required aggregate provenance, and absence of source IDs, exact coordinates, timestamps, and user-level data.
- API contract tests will extend the existing FastAPI/TestClient precedent. They will verify safe candidate provenance fields, ranking determinism, explicit-choice dominance, weekend-only adjustment, sparse-history fallback, validation failures, and absence of forbidden raw fields.
- Ranking behavior tests will verify that familiar and discovery modes produce visibly different orderings over the same data-derived candidate pool and that explanations correctly distinguish profile entropy, aggregate candidate novelty, and category familiarity.
- Frontend tests will extend the existing Vitest and Testing Library suite for initial state, request payloads, returned order, explanations, loading, API failure/retry, keyboard controls, and live update messaging.
- Build acceptance will verify that the website compiles using only committed generated artifacts and does not require the raw dataset or a running API for the static analysis route.
- Accessibility acceptance will cover heading order, landmark and link names, disclosure semantics, visible keyboard focus, non-color state labels, chart alternatives, live rerank announcements, reduced motion, and no horizontal overflow at the target narrow viewport.
- Manual acceptance will compare the notebook and website’s key metrics and chart captions, run the Familiar-to-Something-new rerank, inspect a candidate provenance explanation, test the sparse profile, and repeat the core journey on desktop, mobile, and keyboard.

## Out of Scope

- Replacing or deleting the executed notebook.
- Executing the full analysis during a frontend build or API request.
- A second independently authored set of analytical metrics or conclusions.
- Training, validating, or claiming performance for a recommender model.
- Collaborative filtering, embeddings, personalization learned from real users, or causal inference.
- Presenting user entropy as a venue score, quality score, personality label, or known preference.
- Claiming a historical venue is newly opened, currently operating, popular today, or suitable for a real trip.
- Recovering venue names through scraping, geocoding, or an external Foursquare API.
- Exposing source venue IDs, raw user IDs, exact coordinates, private-home records, timestamps, or trajectories.
- Maps, live location, route planning, authentication, persistence, accounts, external venue APIs, real-time ingestion, or production deployment infrastructure.
- Redesigning the analytical methodology or adding new statistical claims beyond the executed notebook.
- Recommendation-effectiveness claims without a future controlled experiment.

## Further Notes

- The most important terminology correction is: entropy is calculated from a user’s distribution of observed visits. It can influence how strongly a discovery ranker explores, but it does not identify which venue is “fresh.” Candidate novelty needs its own definition.
- The dataset contains venue IDs, category metadata, coordinates, and check-ins, but no human-readable venue names. Data relevance should therefore come from an honest data-derived catalog and aggregate provenance, not fabricated names.
- The safe candidate catalog is a derived demonstration artifact, not a publishable venue directory. The historical and selection-bias limitations must remain visible.
- The preferred test seams are the rendered case-study/prototype journey, the generated-artifact contract, and the API contract. These match existing frontend and backend test conventions while adding only one new seam for deterministic generation.
