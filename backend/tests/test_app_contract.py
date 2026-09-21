"""Application contract tests.

These exist because byte-compiling is not importing. `python -m compileall`
accepts any file that is syntactically valid Python, so a router importing a
module that does not exist, or calling a framework API that has been removed,
compiles cleanly and still takes the whole application down at startup.

Importing `server` is the cheapest check that actually exercises the wiring:
every router registered on the app is imported, every dependency resolves, and
every route decorator runs.
"""

import pytest


@pytest.fixture(scope="module")
def app():
    """The real FastAPI application, imported the way uvicorn imports it."""
    import server

    return server.app


def test_application_imports(app):
    """The app object is constructed and carries routes.

    Fails on any unresolvable import or bad decorator argument in any module
    reachable from `server`, which is the failure `compileall` cannot see.
    """
    assert app.routes, "application exposes no routes"


def test_no_double_api_prefix(app):
    """No route is mounted under `/api/api`.

    `api_router` already carries `prefix="/api"`, so a router that declares
    `prefix="/api/..."` of its own is mounted one level too deep. The endpoints
    still exist, so nothing raises -- they are simply unreachable at the path
    the frontend calls, and every request 404s.
    """
    doubled = sorted(
        route.path
        for route in app.routes
        if getattr(route, "path", "").startswith("/api/api")
    )
    assert not doubled, (
        "routers must declare a bare prefix (e.g. '/startup-copilot'); "
        f"api_router adds '/api'. Doubled paths: {doubled}"
    )


@pytest.mark.parametrize("field", ["model", "force_model"])
def test_google_models_blocked_at_api_boundary(app, field):
    """A Google/Gemini override is refused before any engine sees it.

    Most engines still carry a gemini entry in their own MODEL_CONFIG and do not
    call enforce_approved_model themselves, so this middleware is the boundary
    that actually holds the policy. It must keep failing closed.
    """
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.post(
        "/api/core/execute", json={"goal": "x", field: "gemini-3-flash"}
    )

    assert response.status_code == 400, (
        f"a blocked model passed through '{field}' with "
        f"{response.status_code}; the policy middleware must fail closed"
    )
    assert response.json().get("code") == "MODEL_POLICY_BLOCKED"


def test_unapproved_model_blocked_at_api_boundary(app):
    """A model outside the approved stack is refused, not silently rerouted."""
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.post(
        "/api/core/execute", json={"goal": "x", "force_model": "llama-3-70b"}
    )

    assert response.status_code == 400
    assert response.json().get("code") == "MODEL_POLICY_UNAPPROVED"


def test_no_duplicate_route_registrations(app):
    """No method+path pair is registered by two different handlers.

    Starlette matches the FIRST route whose path matches, so a second
    registration of the same method and path is dead code that never runs. That
    is silent: the app starts, the endpoint answers, and only the wrong handler
    replies.

    This bit `GET /api/health` for a long time. routers/engines/core.py declared
    a bare "/health" while its four sibling routes all declared "/core/...", so
    with that router mounted without a prefix it landed on /api/health and, by
    registering earlier, shadowed server.py's handler entirely.
    """
    from collections import Counter

    registrations = Counter(
        (method, route.path)
        for route in app.routes
        for method in (getattr(route, "methods", None) or ())
        if getattr(route, "path", None)
    )
    duplicates = sorted(
        f"{method} {path} (registered {count}x)"
        for (method, path), count in registrations.items()
        if count > 1
    )
    assert not duplicates, (
        "a second registration of the same method+path never runs -- Starlette "
        f"matches the first. Duplicates: {duplicates}"
    )


def test_api_health_still_serves_what_the_frontend_reads(app):
    """`/api/health` keeps the keys the frontend renders from.

    HomePage reads `status`, `engines` and `models`; EnginesPage builds its whole
    table from `engines`. Both swallow a missing key (`|| []`, `?.`), so dropping
    one does not error -- it silently renders an empty dashboard. server.py's
    handler delegates to the pipeline health function to keep these present.
    """
    from fastapi.testclient import TestClient

    body = TestClient(app).get("/api/health").json()

    assert body.get("status") == "healthy"
    assert body.get("engines"), "HomePage and EnginesPage both render `engines`"
    assert body.get("models"), "HomePage renders a chip per entry in `models`"


# One assertion is deliberately NOT included here yet, because it fails on a
# pre-existing condition and failing the build on it would block unrelated work:
#
#   * engine-level model policy -- only strategy_engine, router and plan_builder
#     call enforce_approved_model. Thirteen other engines carry a "gemini" entry
#     in MODEL_CONFIG with no policy call. Unreachable over HTTP thanks to the
#     middleware above, but reachable by any in-process caller.
