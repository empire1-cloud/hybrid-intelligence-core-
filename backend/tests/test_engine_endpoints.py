"""API contract tests for the hosted Hybrid Intelligence Core.

Executable engine routes are subscription-gated. Set HIC_TEST_TOKEN and
HIC_TEST_TEAM_ID to exercise authenticated responses against a deployed test
instance; without them, these tests verify that the routes fail closed.
"""

import os

import pytest
import requests


BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
TEST_TOKEN = os.environ.get("HIC_TEST_TOKEN", "")
TEST_TEAM_ID = os.environ.get("HIC_TEST_TEAM_ID", "")

pytestmark = pytest.mark.skipif(not BASE_URL, reason="REACT_APP_BACKEND_URL is not configured")


def auth_headers():
    headers = {"Content-Type": "application/json"}
    if TEST_TOKEN:
        headers["Authorization"] = f"Bearer {TEST_TOKEN}"
    if TEST_TEAM_ID:
        headers["X-Team-ID"] = TEST_TEAM_ID
    return headers


def assert_protected_get(path, required_keys=None):
    response = requests.get(f"{BASE_URL}{path}", headers=auth_headers(), timeout=30)

    if not TEST_TOKEN:
        assert response.status_code == 401
        return

    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, dict)
    for key in required_keys or []:
        assert key in data


class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = requests.get(f"{BASE_URL}/api/health", timeout=30)
        assert response.status_code == 200

    def test_health_returns_engine_catalog(self):
        response = requests.get(f"{BASE_URL}/api/health", timeout=30)
        data = response.json()

        assert data["status"] == "healthy"
        assert data["model_policy"] == "approved-non-google-only"
        assert len(data["engines"]) == 19

        expected_engines = {
            "hybrid_intelligence_core",
            "routing_engine",
            "strategy_engine",
            "plan_builder_engine",
            "analysis_engine",
            "opportunity_mapper_engine",
            "evaluator_engine",
            "pricing_engine",
            "blueprint_engine",
            "persona_engine",
            "anime_character_engine",
            "anime_lore_engine",
            "anime_story_engine",
            "art_direction_engine",
            "money_pipeline_engine",
            "pipeline_composer_engine",
            "canon_enforcer",
            "drift_monitor",
            "error_handler",
        }
        assert expected_engines == set(data["engines"])

    def test_health_exposes_only_approved_models(self):
        response = requests.get(f"{BASE_URL}/api/health", timeout=30)
        models = response.json()["models"]

        assert models["gpt-5.2"] == "available"
        assert models["gpt-4o-mini"] == "available"
        assert models["claude-sonnet-4.5"] == "available"
        assert not any("gemini" in model.lower() for model in models)
        assert not any("google" in model.lower() for model in models)
        assert not any("vertex" in model.lower() for model in models)


class TestSubscriptionGate:
    @pytest.mark.parametrize(
        "path",
        [
            "/api/art-direction/styles",
            "/api/art-direction/color-moods",
            "/api/anime/genres",
            "/api/anime/archetypes",
            "/api/pipeline/engines",
            "/api/pipeline/templates",
            "/api/evaluate/presets",
            "/api/pricing/models",
            "/api/blueprint/component-types",
            "/api/persona/templates",
            "/api/core/log",
            "/api/drift-report",
        ],
    )
    def test_engine_reads_require_workspace_or_api_key(self, path):
        assert_protected_get(path)

    def test_core_status_remains_public(self):
        response = requests.get(f"{BASE_URL}/api/core/status", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data["model_policy"] == "approved-non-google-only"


class TestExecutableEndpoints:
    @pytest.mark.parametrize(
        "path,payload",
        [
            ("/api/art-direction", {"project": "TEST_art_project", "genre": "anime", "mood": "dramatic", "model": "gpt-4o-mini"}),
            ("/api/anime/lore", {"world_concept": "TEST_world_concept", "genre": "shonen", "model": "gpt-4o-mini"}),
            ("/api/anime/story", {"concept": "TEST_story_concept", "genre": "shonen", "model": "gpt-4o-mini"}),
            ("/api/money-pipeline", {"idea": "TEST subscription product", "model": "gpt-4o-mini"}),
        ],
    )
    def test_engine_route_exists_and_is_gated(self, path, payload):
        response = requests.post(
            f"{BASE_URL}{path}",
            json=payload,
            headers=auth_headers(),
            timeout=120,
        )

        assert response.status_code != 404, f"Endpoint not found: {path}"
        assert response.status_code != 422, response.text

        if not TEST_TOKEN:
            assert response.status_code == 401

    def test_blocked_model_fails_before_execution(self):
        response = requests.post(
            f"{BASE_URL}/api/money-pipeline",
            json={"idea": "TEST", "model": "gemini-3-flash"},
            headers=auth_headers(),
            timeout=30,
        )
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "MODEL_POLICY_BLOCKED"


class TestBillingCatalog:
    def test_public_plan_catalog_is_monthly_and_no_lockin(self):
        response = requests.get(f"{BASE_URL}/api/billing/plans", timeout=30)
        assert response.status_code == 200

        plans = {plan["key"]: plan for plan in response.json()["plans"]}
        assert set(plans) == {"free", "pro", "enterprise"}
        assert plans["free"]["price_display"] == "$0/month"
        assert plans["pro"]["price_display"] == "$299/month"
        assert plans["enterprise"]["price_display"] == "Starting at $1,500/month"

        for plan in plans.values():
            assert plan["billing_interval"] == "month"
            assert plan["contract_term"] == "month_to_month"
            assert plan["cancel_anytime"] is True

        assert plans["pro"]["limits"]["executions_per_month"] == 5000
        assert plans["enterprise"]["limits"]["executions_per_month"] == 50000
        assert plans["enterprise"]["requires_sales"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
