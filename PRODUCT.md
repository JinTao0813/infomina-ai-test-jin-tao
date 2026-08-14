# Product

<!-- impeccable:product-schema 1 -->

## Platform

Web: Next.js App Router with React and TypeScript; FastAPI and Pydantic; committed generated artifacts. Local execution is sufficient.

## Users

Interview reviewers assessing data-science reasoning, product judgment, privacy boundaries, and engineering range. They need to understand the complete path from historical evidence to a cautious, testable product hypothesis.

## Product Purpose

**From Data to Product** joins the authoritative location-entropy analysis and **Context-Aware Discovery** prototype into one case study. The analysis route renders a deterministic presentation artifact generated from the executed notebook. Discovery Mode lets reviewers change a synthetic profile, temporal context, and explicit preference, then inspect deterministic reranking over privacy-safe, data-derived historical candidates.

Success means reviewers can follow: data provenance → preparation → metric → findings → limits → opportunity comparison → selected hypothesis → interactive behavior → evaluation plan, without mistaking entropy for a venue score or the prototype for a validated recommender.

## Positioning

The project distinguishes three concepts:

1. normalized venue/category entropy describes diversity in an observed synthetic profile history;
2. aggregate candidate novelty is inverse popularity in the historical sample;
3. category familiarity indicates whether the candidate category appears in that synthetic profile history.

Explicit intent remains the strongest ranking input.

## Operating Context

Reviewers open `/` for the generated case study and `/prototype/discovery` for the interactive hypothesis. The static analysis route requires neither FastAPI nor raw data. Discovery Mode requires the local API. Offline generation alone reads the executed notebook or source check-ins.

## Capabilities and Constraints

- Executed notebook remains authoritative and downloadable.
- Generated analysis artifact preserves narrative, equations, aggregate tables, charts, and collapsible code.
- Artifact metadata exposes source path, execution-derived generation time, and source fingerprint.
- Four anonymous synthetic profiles; no real source users.
- Candidate catalog aggregates actual historical NYC/Tokyo venue records under minimum-support and sensitive-category exclusions.
- Source dataset has no venue names; candidates use city/category/number pseudonyms.
- No source venue IDs, user IDs, exact coordinates, timestamps, trajectories, private-home candidates, maps, live venue data, persistence, authentication, external APIs, or trained model.
- “New” means new to the synthetic profile or less commonly visited in the historical sample—not newly opened.
- Sparse history uses confidence-adjusted neutral fallback; explicit intent dominates inferred behavior.
- Historical candidates are not a current venue directory and may no longer exist.

## Brand Commitments

Clear, cautious, evidence-led voice. Observations, interpretations, hypotheses, implementation choices, and limits remain visually distinguishable. Persistent claim boundary: illustrative ranking over privacy-safe historical candidates; not a trained or validated recommender or current place guide.

## Evidence on Hand

The executed notebook provides aggregate findings: similar city medians; higher weekend entropy for most eligible users; distinct venue/category diversity; and observation-count dependence. No customer claims, outcome evidence, current venue evidence, or recommendation-effectiveness evidence exists.

## Product Principles

1. Explicit intent beats inferred defaults.
2. Profile metrics and candidate signals remain separate and named.
3. Explain behavior without turning metrics into identity or quality.
4. Show uncertainty and fall back neutrally when evidence is sparse.
5. Minimize and aggregate source data before it reaches product surfaces.
6. Treat the prototype as a hypothesis requiring randomized evaluation.

## Accessibility & Inclusion

Semantic headings and landmarks, keyboard-operable navigation and controls, accessible disclosures, visible focus, table captions, chart alternatives, live reranking announcements, WCAG AA contrast, reduced-motion support, and usable layouts around 375px and 1440px.
