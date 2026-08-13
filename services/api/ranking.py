"""Transparent deterministic ranking policy for fictional candidates."""

from collections.abc import Sequence

from services.api.schemas import (
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
    """Apply the documented confidence and context adjustments."""
    inferred_discovery = 0.60 * profile.venue_entropy + 0.40 * profile.category_entropy
    confidence_adjusted = (
        profile.confidence * inferred_discovery
        + (1 - profile.confidence) * 0.50
    )
    context_adjustment = (
        profile.confidence * profile.weekend_delta
        if context is Context.WEEKEND
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
    """Rank candidates by score descending and stable ID ascending."""
    applied_discovery = calculate_applied_discovery(
        profile, context, discovery_mode
    )
    scored_candidates = [
        (
            _calculate_final_score(candidate, applied_discovery),
            candidate,
        )
        for candidate in candidates
    ]
    scored_candidates.sort(key=lambda item: (-item[0], item[1].id))
    return [
        _format_recommendation(
            profile,
            candidate,
            context,
            discovery_mode,
            exact_score,
        )
        for exact_score, candidate in scored_candidates[:limit]
    ]


def ranking_summary(
    profile: Profile, context: Context, discovery_mode: DiscoveryMode
) -> str:
    if profile.confidence < SPARSE_CONFIDENCE_THRESHOLD:
        return (
            "Limited history shifts the inferred signal toward a neutral starting "
            "point; your explicit choice remains the strongest input."
        )
    if context is Context.WEEKEND and profile.weekend_delta > 0:
        return (
            "Your choice leads, with a modest weekend adjustment supported by this "
            "synthetic profile’s observed pattern."
        )
    if discovery_mode is DiscoveryMode.FAMILIAR:
        return "Your familiar choice emphasizes baseline relevance over novelty."
    if discovery_mode is DiscoveryMode.SOMETHING_NEW:
        return "Your discovery choice gives venue and activity novelty more weight."
    return "Your balanced choice combines relevance with measured venue and activity novelty."


def _calculate_final_score(
    candidate: CandidateVenue, applied_discovery: float
) -> float:
    novelty_score = 0.60 * candidate.venue_novelty + 0.40 * candidate.category_novelty
    return (
        (1 - applied_discovery) * candidate.baseline_relevance
        + applied_discovery * novelty_score
        - 0.15 * candidate.distance_penalty
    )


def _format_recommendation(
    profile: Profile,
    candidate: CandidateVenue,
    context: Context,
    discovery_mode: DiscoveryMode,
    exact_score: float,
) -> Recommendation:
    novelty_score = 0.60 * candidate.venue_novelty + 0.40 * candidate.category_novelty
    return Recommendation(
        **candidate.model_dump(),
        final_score=round(exact_score, 4),
        novelty_score=round(novelty_score, 4),
        reason=_explain(profile, candidate, context, discovery_mode),
    )


def _explain(
    profile: Profile,
    candidate: CandidateVenue,
    context: Context,
    discovery_mode: DiscoveryMode,
) -> str:
    if profile.confidence < SPARSE_CONFIDENCE_THRESHOLD:
        return "Using a neutral starting point because this demo profile has limited history."
    if discovery_mode is DiscoveryMode.FAMILIAR and candidate.baseline_relevance >= 0.75:
        return "Prioritized for relevance because you chose to keep it familiar."
    if (
        candidate.category in profile.familiar_categories
        and candidate.venue_novelty >= 0.55
    ):
        return "A new venue in a familiar activity category."
    if candidate.category_novelty >= 0.65 and context is Context.WEEKEND:
        return "A broader activity choice for your weekend setting."
    if candidate.category_novelty >= 0.65:
        return "A different kind of activity, surfaced because discovery has more weight."
    return "Balances baseline relevance with a measured amount of venue novelty."
