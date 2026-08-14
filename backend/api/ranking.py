"""Transparent deterministic policy over privacy-safe historical candidates."""

from collections.abc import Sequence

from backend.api.schemas import (
    CandidateVenue,
    Context,
    DiscoveryMode,
    Profile,
    Recommendation,
)

EXPLICIT_DISCOVERY = {
    DiscoveryMode.FAMILIAR: 0.20,
    DiscoveryMode.BALANCED: 0.50,
    DiscoveryMode.SOMETHING_NEW: 0.80,
}
SPARSE_CONFIDENCE_THRESHOLD = 0.50


def calculate_applied_discovery(
    profile: Profile, context: Context, discovery_mode: DiscoveryMode
) -> float:
    """Apply documented confidence and context adjustments."""
    inferred_discovery = 0.60 * profile.venue_entropy + 0.40 * profile.category_entropy
    is_sparse = profile.confidence < SPARSE_CONFIDENCE_THRESHOLD
    confidence_adjusted = (
        0.50
        if is_sparse
        else profile.confidence * inferred_discovery
        + (1 - profile.confidence) * 0.50
    )
    context_adjustment = (
        profile.confidence * profile.weekend_delta
        if context is Context.WEEKEND and not is_sparse
        else 0.0
    )
    applied = (
        0.70 * EXPLICIT_DISCOVERY[discovery_mode]
        + 0.30 * confidence_adjusted
        + context_adjustment
    )
    return min(1.0, max(0.0, applied))


def rank_candidates(
    *,
    profile: Profile,
    candidates: Sequence[CandidateVenue],
    context: Context,
    discovery_mode: DiscoveryMode,
    limit: int,
) -> list[Recommendation]:
    """Rank candidates by exact score descending and stable generated ID ascending."""
    applied_discovery = calculate_applied_discovery(
        profile, context, discovery_mode
    )
    scored_candidates = [
        (_calculate_final_score(profile, candidate, applied_discovery), candidate)
        for candidate in candidates
    ]
    scored_candidates.sort(key=lambda item: (-item[0], item[1].id))
    return [
        _format_recommendation(
            profile, candidate, context, discovery_mode, exact_score
        )
        for exact_score, candidate in scored_candidates[:limit]
    ]


def ranking_summary(
    profile: Profile, context: Context, discovery_mode: DiscoveryMode
) -> str:
    if profile.confidence < SPARSE_CONFIDENCE_THRESHOLD:
        return (
            "Limited history shifts the inferred profile signal toward neutral; "
            "your explicit choice remains the strongest input."
        )
    if context is Context.WEEKEND and profile.weekend_delta > 0:
        return (
            "Your choice leads, with a modest weekend adjustment supported only "
            "by this synthetic profile’s observed history."
        )
    if discovery_mode is DiscoveryMode.FAMILIAR:
        return "Your familiar choice emphasizes aggregate historical popularity."
    if discovery_mode is DiscoveryMode.SOMETHING_NEW:
        return (
            "Your discovery choice gives inverse historical popularity and "
            "unfamiliar categories more weight."
        )
    return (
        "Your balanced choice combines aggregate historical popularity with "
        "candidate novelty and category familiarity."
    )


def _category_familiarity(profile: Profile, candidate: CandidateVenue) -> int:
    return int(candidate.category in profile.familiar_categories)


def _novelty_score(profile: Profile, candidate: CandidateVenue) -> float:
    category_discovery = 1 - _category_familiarity(profile, candidate)
    return 0.65 * candidate.aggregate_novelty + 0.35 * category_discovery


def _calculate_final_score(
    profile: Profile, candidate: CandidateVenue, applied_discovery: float
) -> float:
    # The curve keeps familiar mode relevance-led while allowing the explicit
    # discovery choice to produce a clear ranking change.
    novelty_weight = applied_discovery**1.5
    return (
        (1 - novelty_weight) * candidate.baseline_relevance
        + novelty_weight * _novelty_score(profile, candidate)
    )


def _format_recommendation(
    profile: Profile,
    candidate: CandidateVenue,
    context: Context,
    discovery_mode: DiscoveryMode,
    exact_score: float,
) -> Recommendation:
    familiarity = _category_familiarity(profile, candidate)
    return Recommendation(
        **candidate.model_dump(),
        final_score=round(exact_score, 4),
        category_familiarity=familiarity,
        category_discovery=1 - familiarity,
        novelty_score=round(_novelty_score(profile, candidate), 4),
        reason=_explain(profile, candidate, context, discovery_mode),
    )


def _explain(
    profile: Profile,
    candidate: CandidateVenue,
    context: Context,
    discovery_mode: DiscoveryMode,
) -> str:
    if profile.confidence < SPARSE_CONFIDENCE_THRESHOLD:
        return (
            "Neutral profile fallback: limited history means your explicit choice "
            "does most of the work."
        )
    familiar = bool(_category_familiarity(profile, candidate))
    if discovery_mode is DiscoveryMode.FAMILIAR and candidate.baseline_relevance >= 0.75:
        return (
            "Higher aggregate popularity in the historical sample supports your "
            "familiar choice."
        )
    if familiar and candidate.aggregate_novelty >= 0.5:
        return (
            "Less commonly visited in this historical sample, within a category "
            "familiar to the synthetic profile."
        )
    if not familiar and context is Context.WEEKEND:
        return (
            "A category outside this synthetic profile’s familiar history, with "
            "a modest weekend adjustment."
        )
    if not familiar:
        return (
            "A category outside this synthetic profile’s familiar history, surfaced "
            "as a separate discovery signal."
        )
    return (
        "Balances aggregate historical popularity with candidate novelty; the "
        "category is familiar to this synthetic profile."
    )
