"""
Canon router wiring test.

Same technique as `test_app_contract.py`: import the real `server.app` the
way uvicorn does and assert on its route table. `test_app_contract.py::
test_no_double_api_prefix` already covers every route including these; this
file additionally pins the exact paths so a future refactor that silently
drops or renames one of the new canon endpoints fails a test instead of only
being noticed by an operator.
"""

import pytest


@pytest.fixture(scope="module")
def app():
    import server

    return server.app


EXPECTED_CANON_PATHS = {
    ("POST", "/api/canon/execute"),
    ("GET", "/api/canon/runs"),
    ("GET", "/api/canon/runs/{run_id}"),
    ("DELETE", "/api/canon/runs/{run_id}"),
    ("GET", "/api/canon/status"),
}


def test_canon_routes_are_registered_under_api_prefix(app):
    registered = {
        (method, route.path)
        for route in app.routes
        if hasattr(route, "methods")
        for method in route.methods
        if method != "HEAD"
    }

    missing = EXPECTED_CANON_PATHS - registered
    assert not missing, f"expected canon routes missing from the app: {missing}"


def test_core_execute_route_is_still_present(app):
    """The new canon path is additive -- /core/execute must be untouched."""
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/api/core/execute" in paths
    assert "/api/core/strategy-to-plan" in paths
    assert "/api/core/status" in paths
