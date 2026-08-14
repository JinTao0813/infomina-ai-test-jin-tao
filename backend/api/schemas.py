"""Public schemas for the privacy-safe Discovery Mode API."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Context(StrEnum):
    WEEKDAY = "weekday"
    WEEKEND = "weekend"


class DiscoveryMode(StrEnum):
    FAMILIAR = "familiar"
    BALANCED = "balanced"
    SOMETHING_NEW = "something_new"


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    venue_entropy: float = Field(ge=0, le=1)
    category_entropy: float = Field(ge=0, le=1)
    weekend_delta: float = Field(ge=-1, le=1)
    observation_count: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    familiar_categories: list[str]


class CandidateVenue(BaseModel):
    """Aggregate candidate fields safe to expose to the browser."""

    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    city: str
    category: str
    historical_checkins: int = Field(ge=0)
    distinct_historical_visitors: int = Field(ge=0)
    aggregate_popularity_percentile: int = Field(ge=0, le=100)
    baseline_relevance: float = Field(ge=0, le=1)
    aggregate_novelty: float = Field(ge=0, le=1)
    provenance: str


class RecommendationRequest(BaseModel):
    profile_id: str
    context: Context
    discovery_mode: DiscoveryMode
    limit: int = Field(default=6, ge=1, le=12)


class Recommendation(CandidateVenue):
    final_score: float
    category_familiarity: int = Field(ge=0, le=1)
    category_discovery: int = Field(ge=0, le=1)
    novelty_score: float = Field(ge=0, le=1)
    reason: str


class RecommendationResponse(BaseModel):
    profile: Profile
    context: Context
    discovery_mode: DiscoveryMode
    applied_discovery: float
    uses_neutral_fallback: bool
    ranking_summary: str
    recommendations: list[Recommendation]
    disclaimer: str
