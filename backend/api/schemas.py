"""Public schemas for the synthetic Discovery Mode API."""

from enum import StrEnum

from pydantic import BaseModel, Field


class Context(StrEnum):
    WEEKDAY = "weekday"
    WEEKEND = "weekend"


class DiscoveryMode(StrEnum):
    FAMILIAR = "familiar"
    BALANCED = "balanced"
    SOMETHING_NEW = "something_new"


class Profile(BaseModel):
    id: str
    label: str
    venue_entropy: float = Field(ge=0, le=1)
    category_entropy: float = Field(ge=0, le=1)
    weekend_delta: float = Field(ge=-1, le=1)
    observation_count: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    familiar_categories: list[str]


class CandidateVenue(BaseModel):
    id: str
    name: str
    category: str
    description: str
    baseline_relevance: float = Field(ge=0, le=1)
    venue_novelty: float = Field(ge=0, le=1)
    category_novelty: float = Field(ge=0, le=1)
    distance_penalty: float = Field(ge=0, le=1)


class RecommendationRequest(BaseModel):
    profile_id: str
    context: Context
    discovery_mode: DiscoveryMode
    limit: int = Field(default=6, ge=1, le=12)


class Recommendation(BaseModel):
    id: str
    name: str
    category: str
    description: str
    final_score: float
    baseline_relevance: float
    venue_novelty: float
    category_novelty: float
    novelty_score: float
    distance_penalty: float
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
