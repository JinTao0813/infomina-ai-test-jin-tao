"""FastAPI application serving safe profiles and aggregate candidates."""

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.api.ranking import (
    SPARSE_CONFIDENCE_THRESHOLD,
    calculate_applied_discovery,
    rank_candidates,
    ranking_summary,
)
from backend.api.schemas import (
    CandidateVenue,
    Profile,
    RecommendationRequest,
    RecommendationResponse,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"
DISCLAIMER = (
    "Illustrative discovery ranking over privacy-safe historical candidates; "
    "not a trained or validated recommender or current place guide."
)


def _load_fixture(filename: str, schema: type[Profile] | type[CandidateVenue]):
    payload = json.loads((FIXTURE_DIR / filename).read_text(encoding="utf-8"))
    return [schema.model_validate(item) for item in payload]


PROFILES = _load_fixture("profiles.json", Profile)
VENUES = _load_fixture("venues.json", CandidateVenue)
PROFILES_BY_ID = {profile.id: profile for profile in PROFILES}

app = FastAPI(
    title="Context-Aware Discovery prototype API",
    version="0.1.0",
    description=DISCLAIMER,
)

origins = [
    origin.strip()
    for origin in os.getenv(
        "DISCOVERY_FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/profiles", response_model=list[Profile])
def profiles() -> list[Profile]:
    return PROFILES


@app.get("/venues", response_model=list[CandidateVenue])
def venues() -> list[CandidateVenue]:
    return VENUES


@app.post("/recommendations", response_model=RecommendationResponse)
def recommendations(request: RecommendationRequest) -> RecommendationResponse:
    profile = PROFILES_BY_ID.get(request.profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Unknown synthetic profile")

    applied = calculate_applied_discovery(
        profile, request.context, request.discovery_mode
    )
    return RecommendationResponse(
        profile=profile,
        context=request.context,
        discovery_mode=request.discovery_mode,
        applied_discovery=round(applied, 4),
        uses_neutral_fallback=profile.confidence < SPARSE_CONFIDENCE_THRESHOLD,
        ranking_summary=ranking_summary(
            profile, request.context, request.discovery_mode
        ),
        recommendations=rank_candidates(
            profile=profile,
            candidates=VENUES,
            context=request.context,
            discovery_mode=request.discovery_mode,
            limit=request.limit,
        ),
        disclaimer=DISCLAIMER,
    )
