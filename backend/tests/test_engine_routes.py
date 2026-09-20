"""Regression tests for the HIC engine HTTP route contract.

The Engines UI calls the canonical /api/<engine-path> endpoints.  The app-level
/api prefix is owned by server.py, so engine routers must not add another /api
prefix and the legacy /api/engines/<name>/test paths must not be required.
"""

import pytest


CANONICAL_ENGINE_ROUTES = {
    "/api/core/execute",
    "/api/route",
    "/api/strategy",
    "/api/plan",
    "/api/analyze",
    "/api/opportunities",
    "/api/evaluate",
    "/api/pricing",
    "/api/blueprint",
    "/api/persona",
    "/api/anime/character",
    "/api/anime/lore",
    "/api/anime/story",
    "/api/art-direction",
    "/api/money-pipeline",
    "/api/pipeline/compose",
    "/api/drift-report",
}

LEGACY_FRONTEND_ROUTES = {
    "/api/engines/strategy/test",
    "/api/engines/plan/test",
    "/api/engines/analysis/test",
    "/api/engines/opportunity/test",
    "/api/engines/evaluator/test",
    "/api/engines/pricing/test",
    "/api/engines/blueprint/test",
    "/api/engines/persona/test",
    "/api/engines/anime/character/test",
    "/api/engines/anime/lore/test",
    "/api/engines/anime/story/test",
    "/api/engines/art-direction/test",
    "/api/engines/money-pipeline/test",
    "/api/engines/pipeline/compose/test",
}


@pytest.fixture(scope="module")
def app():
    import server

    return server.app


def _route_paths(app):
    return {
        route.path
        for route in app.routes
        if getattr(route, "path", None)
    }


def test_canonical_engine_routes_are_mounted(app):
    paths = _route_paths(app)
    missing = sorted(CANONICAL_ENGINE_ROUTES - paths)
    assert not missing, f"Engine UI contract routes are missing: {missing}"


def test_legacy_engine_test_routes_are_not_mounted(app):
    paths = _route_paths(app)
    unexpected = sorted(LEGACY_FRONTEND_ROUTES & paths)
    assert not unexpected, (
        "Legacy /api/engines/*/test routes are mounted unexpectedly: "
        f"{unexpected}"
    )


def test_engine_routes_do_not_double_prefix_api(app):
    doubled = sorted(
        path for path in _route_paths(app) if path.startswith("/api/api/")
    )
    assert not doubled, f"Double-prefixed engine routes found: {doubled}"


@pytest.mark.parametrize(
    "path",
    sorted(CANONICAL_ENGINE_ROUTES),
)
def test_canonical_routes_are_unique(app, path):
    matches = [
        route
        for route in app.routes
        if getattr(route, "path", None) == path
    ]
    assert len(matches) == 1, (
        f"{path} should have exactly one registered route; found {len(matches)}"
    )
