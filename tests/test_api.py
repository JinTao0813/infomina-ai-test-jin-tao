import pytest
from fastapi.testclient import TestClient

from services.api.main import app
from services.api.ranking import calculate_applied_discovery, rank_candidates
from services.api.schemas import CandidateVenue, Context, DiscoveryMode, Profile


@pytest.fixture
def routine_profile() -> Profile:
    return Profile(
        id="routine",
        label="Routine-oriented demo",
        venue_entropy=0.72,
        category_entropy=0.58,
        weekend_delta=0.04,
        observation_count=180,
        confidence=0.90,
        familiar_categories=["Coffee Shop", "Park"],
    )


def test_discovery_level_matches_documented_calculation(
    routine_profile: Profile,
) -> None:
    result = calculate_applied_discovery(
        routine_profile, Context.WEEKEND, DiscoveryMode.BALANCED
    )

    assert result == pytest.approx(0.58028)


def test_explicit_choice_dominates_inferred_default(routine_profile: Profile) -> None:
    familiar = calculate_applied_discovery(
        routine_profile, Context.WEEKDAY, DiscoveryMode.FAMILIAR
    )
    balanced = calculate_applied_discovery(
        routine_profile, Context.WEEKDAY, DiscoveryMode.BALANCED
    )
    new = calculate_applied_discovery(
        routine_profile, Context.WEEKDAY, DiscoveryMode.SOMETHING_NEW
    )

    assert balanced - familiar == pytest.approx(0.21)
    assert new - balanced == pytest.approx(0.21)


def test_weekend_adjustment_is_only_applied_on_weekends(
    routine_profile: Profile,
) -> None:
    weekday = calculate_applied_discovery(
        routine_profile, Context.WEEKDAY, DiscoveryMode.BALANCED
    )
    weekend = calculate_applied_discovery(
        routine_profile, Context.WEEKEND, DiscoveryMode.BALANCED
    )

    assert weekend - weekday == pytest.approx(0.036)


def test_sparse_history_falls_back_toward_neutral() -> None:
    sparse = Profile(
        id="sparse",
        label="New / sparse history demo",
        venue_entropy=0.10,
        category_entropy=0.10,
        weekend_delta=0.40,
        observation_count=8,
        confidence=0.0,
        familiar_categories=[],
    )

    result = calculate_applied_discovery(
        sparse, Context.WEEKEND, DiscoveryMode.BALANCED
    )

    assert result == pytest.approx(0.50)


def test_ranking_is_deterministic_and_candidate_id_breaks_ties(
    routine_profile: Profile,
) -> None:
    candidates = [
        CandidateVenue(
            id=candidate_id,
            name=candidate_id,
            category="Park",
            description="Fictional venue.",
            baseline_relevance=0.7,
            venue_novelty=0.5,
            category_novelty=0.5,
            distance_penalty=0.2,
        )
        for candidate_id in ["venue-b", "venue-a"]
    ]

    result = rank_candidates(
        profile=routine_profile,
        candidates=candidates,
        context=Context.WEEKDAY,
        discovery_mode=DiscoveryMode.BALANCED,
        limit=2,
    )

    assert [item.id for item in result] == ["venue-a", "venue-b"]


client = TestClient(app)


def test_recommendations_validate_request_and_unknown_profile() -> None:
    invalid = client.post(
        "/recommendations",
        json={
            "profile_id": "routine",
            "context": "holiday",
            "discovery_mode": "balanced",
            "limit": 13,
        },
    )
    missing = client.post(
        "/recommendations",
        json={
            "profile_id": "not-real",
            "context": "weekday",
            "discovery_mode": "balanced",
            "limit": 6,
        },
    )

    assert invalid.status_code == 422
    assert missing.status_code == 404


def test_recommendations_are_safe_and_explainable() -> None:
    response = client.post(
        "/recommendations",
        json={
            "profile_id": "mixed",
            "context": "weekday",
            "discovery_mode": "balanced",
            "limit": 6,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["recommendations"]) == 6
    assert payload["disclaimer"].startswith("Illustrative ranking")
    assert all(item["reason"] for item in payload["recommendations"])
    forbidden = {"user_id", "venue_id", "latitude", "longitude", "coordinates"}
    assert forbidden.isdisjoint(_all_keys(payload))


def test_explicit_modes_visibly_rerank_the_shared_candidate_pool() -> None:
    def request(mode: str) -> list[str]:
        response = client.post(
            "/recommendations",
            json={
                "profile_id": "mixed",
                "context": "weekday",
                "discovery_mode": mode,
                "limit": 6,
            },
        )
        assert response.status_code == 200
        return [item["name"] for item in response.json()["recommendations"]]

    familiar = request("familiar")
    something_new = request("something_new")

    assert familiar[0] == "Northline Coffee Works"
    assert something_new[0] == "Cloudline Observatory"
    assert familiar != something_new


def test_sparse_profile_returns_neutral_fallback_explanation() -> None:
    response = client.post(
        "/recommendations",
        json={
            "profile_id": "sparse",
            "context": "weekend",
            "discovery_mode": "balanced",
            "limit": 3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["uses_neutral_fallback"] is True
    assert "limited history" in payload["ranking_summary"].lower()
    assert all(
        "limited history" in item["reason"].lower()
        for item in payload["recommendations"]
    )


def _all_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {
            key for child in value.values() for key in _all_keys(child)
        }
    if isinstance(value, list):
        return {key for child in value for key in _all_keys(child)}
    return set()
