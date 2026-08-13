# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Next.js App Router with React and TypeScript; FastAPI and Pydantic; deterministic in-memory synthetic fixtures. Local execution is sufficient.

## Users

Interview reviewers assessing data-science reasoning, product judgment, and engineering range. They operate a short demonstration to understand how evidence becomes a cautious, testable product hypothesis.

## Product Purpose

Context-Aware Discovery extends the authoritative location-entropy analysis into a bounded demonstration. Its Discovery Mode lets reviewers change a synthetic profile, temporal context, and explicit discovery preference, then inspect deterministic reranking and its reasons.

Success means reviewers can follow: observed evidence → cautious interpretation → user need → product hypothesis → interactive behavior → evaluation plan, without mistaking the prototype for a trained or validated recommender.

## Positioning

The prototype makes venue novelty and activity-category novelty separately inspectable, combines them with confidence-aware temporal context, and always gives explicit preference dominant influence.

## Operating Context

Reviewers run a Python API and Next.js frontend locally, open `/prototype/discovery`, change controls, inspect ranking explanations, and read methodology, privacy, and future experiment notes. The executed notebook remains the authoritative analysis.

## Capabilities and Constraints

- Product concept: **Context-Aware Discovery**. Prototype feature: **Discovery Mode**.
- Prompt: “What feels right today?” Choices: Keep it familiar / Balanced / Show me something new.
- Four anonymous synthetic profiles and fictional venue candidates only.
- Transparent deterministic ranker; no training, persistence, authentication, external APIs, maps, source-record browser access, or quality claims.
- Entropy is a ranking signal, never a personality label.
- Sparse history uses confidence-adjusted neutral fallback; explicit intent dominates inferred behavior.
- The API loads safe fixtures at startup and exposes no source IDs, coordinates, or trajectories.
- Prototype is local-only unless deployment is decided later.

## Brand Commitments

Clear, cautious, evidence-led voice. Observations, interpretations, hypotheses, and implementation choices must remain distinguishable. Persistent disclaimer: illustrative ranking over fictional venues; not a validated recommender.

## Evidence on Hand

The executed notebook at `notebooks/location_entropy_analysis.ipynb` provides aggregate findings: similar city medians; higher weekend entropy for most eligible users; distinct venue/category diversity; and observation-count dependence. `PROTOTYPE_SPEC.md` records the exact claim boundary, ranking policy, API contract, UX, safeguards, and acceptance criteria. No customer claims, outcome evidence, or recommendation-effectiveness evidence exists and none may be fabricated.

## Product Principles

1. Explicit intent beats inferred defaults.
2. Explain behavior without turning metrics into identity.
3. Show uncertainty and fall back neutrally when evidence is sparse.
4. Keep synthetic demonstration data separate from source check-ins.
5. Treat the prototype as a hypothesis that requires randomized evaluation.

## Accessibility & Inclusion

Keyboard-operable controls, visible focus, live result announcements, WCAG AA contrast, reduced-motion support, and usable layouts around 375px and 1440px.
