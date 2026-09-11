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

# A duplicate-route assertion is deliberately not included here yet: `GET
# /api/health` is already registered twice on main, and failing the build on a
# pre-existing condition would block unrelated work. Worth fixing separately.
