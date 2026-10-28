"""
End-to-end customer journey over real HTTP routes, in-process.

What this proves: the full FastAPI app (all middleware, dependencies,
routers, services) handles signup -> team -> engine execution -> usage
metering -> team-scoped history -> tenant isolation -> plan limits, with
the real request/response path.

What this does NOT prove (stated, per the repo's working-style rule):
- MongoDB is ``mongomock_motor`` (in-memory), not a real server. Query
  semantics are close but not identical; index creation, the app lifespan
  hook and connection handling are not exercised.
- The LLM is stubbed at ``StrategyEngine._create_chat`` -- no provider call,
  no network. Output quality is not tested.
- Single process. Multi-worker behaviour (gunicorn) is not covered.
"""

import json
import sys
import types

import pytest


def _ensure_emergentintegrations_importable():
    for name in ("emergentintegrations", "emergentintegrations.llm", "emergentintegrations.llm.chat"):
        sys.modules.setdefault(name, types.ModuleType(name))
    chat_mod = sys.modules["emergentintegrations.llm.chat"]
    if not hasattr(chat_mod, "LlmChat"):
        class _MinimalStub:
            def __init__(self, *a, **k):
                pass

            def with_model(self, *a, **k):
                return self

        chat_mod.LlmChat = _MinimalStub
        chat_mod.UserMessage = _MinimalStub


_ensure_emergentintegrations_importable()

VALID_STRATEGY = json.dumps({
    "summary": "Launch in one city first.",
    "steps": ["Pick the city", "Recruit 10 pilot customers"],
    "risks": ["Slow adoption"],
    "resources": ["Two engineers"],
    "next_action": "Email five pilot prospects today.",
})


class _StubChat:
    def __init__(self, response):
        self._response = response

    async def send_message(self, *a, **k):
        return self._response


@pytest.fixture
def app_client(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from mongomock_motor import AsyncMongoMockClient

    import database.connection as connection
    from services import execution_logger
    from services.strategy_engine import StrategyEngine
    import server

    from core.rate_limit import reset_rate_limits

    reset_rate_limits()
    monkeypatch.setattr(connection, "_db", AsyncMongoMockClient()["hic_e2e"])
    # Keep the process-local JSON log out of the repository checkout.
    monkeypatch.setattr(execution_logger, "LOG_FILE", str(tmp_path / "execution_logs.json"))
    # Restored after the test so later tests never persist test entries
    # into the committed execution_logs.json.
    monkeypatch.setattr(execution_logger.get_logger(), "logs", [])

    state = {"response": VALID_STRATEGY}
    monkeypatch.setattr(
        StrategyEngine, "_create_chat",
        classmethod(lambda cls, model=None: _StubChat(state["response"])),
    )
    client = TestClient(server.app)  # no `with`: lifespan (real Mongo connect) is not run
    client.llm = state
    return client


def _signup(client, email):
    resp = client.post("/api/auth/signup", json={
        "email": email, "password": "Correct-Horse-Battery-1!", "first_name": "Test", "last_name": "User",
    })
    assert resp.status_code == 200, resp.text
    body = resp.json()
    team_id = (body.get("current_team") or {}).get("id") or (body.get("current_team") or {}).get("_id")
    if not team_id:
        teams = client.get("/api/teams", headers={"Authorization": f"Bearer {body['access_token']}"}).json()
        team_list = teams.get("teams", teams) if isinstance(teams, dict) else teams
        team_id = team_list[0].get("id") or team_list[0].get("_id")
    return {"Authorization": f"Bearer {body['access_token']}", "X-Team-ID": str(team_id)}, str(team_id)


def _usage(client, headers):
    resp = client.get("/api/billing/usage", headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()["usage"]["executions_count"]


def test_full_customer_journey(app_client):
    client = app_client
    alice, alice_team = _signup(client, "alice@example.com")
    bob, _ = _signup(client, "bob@example.com")

    # Unauthenticated engine call is refused.
    assert client.post("/api/strategy", json={"goal": "grow"}).status_code in (401, 403)

    # A real (stubbed-LLM) execution succeeds and is metered once.
    resp = client.post("/api/strategy", json={"goal": "Grow my bakery"}, headers=alice)
    assert resp.status_code == 200, resp.text
    assert resp.json()["next_action"].startswith("Email five")
    assert _usage(client, alice) == 1

    # It appears in Alice's team-scoped history (previously only /canon did).
    history = client.get("/api/history", headers=alice).json()
    assert history["total"] == 1 and history["logs"][0]["engine"] == "strategy_engine"

    # ...and not in Bob's.
    assert client.get("/api/history", headers=bob).json()["total"] == 0
    assert _usage(client, bob) == 0

    # Bob cannot act inside Alice's team by naming it.
    spoof = {**bob, "X-Team-ID": alice_team}
    assert client.post("/api/strategy", json={"goal": "x"}, headers=spoof).status_code in (401, 403, 404)

    # An unparseable model response is an honest failure and is NOT billed.
    client.llm["response"] = "Sorry, I cannot help."
    failed = client.post("/api/strategy", json={"goal": "Grow my bakery"}, headers=alice)
    assert failed.status_code == 500
    assert _usage(client, alice) == 1
    client.llm["response"] = VALID_STRATEGY

    # Model policy holds over HTTP.
    blocked = client.post("/api/strategy", json={"goal": "x", "force_model": "gemini-3-flash"}, headers=alice)
    assert blocked.status_code == 400 and blocked.json()["code"] == "MODEL_POLICY_BLOCKED"


def test_core_log_does_not_leak_between_teams(app_client):
    client = app_client
    alice, _ = _signup(client, "carol@example.com")
    bob, _ = _signup(client, "dave@example.com")

    assert client.post("/api/core/execute", json={"prompt": "carol's confidential plan"}, headers=alice).status_code == 200
    bob_view = client.get("/api/core/log", headers=bob).json()
    assert all("confidential" not in json.dumps(e) for e in bob_view["log"])
    alice_view = client.get("/api/core/log", headers=alice).json()
    assert any("confidential" in e["prompt_preview"] for e in alice_view["log"])


def test_plan_limit_returns_429_and_cannot_be_exceeded(app_client):
    import asyncio
    from bson import ObjectId
    from database import teams_collection
    from services.billing_service import get_plan_limits

    client = app_client
    erin, team_id = _signup(client, "erin@example.com")
    limit = get_plan_limits("free")["executions_per_month"]

    # First call seeds usage.period_start for the current month.
    assert client.post("/api/strategy", json={"goal": "x"}, headers=erin).status_code == 200
    asyncio.run(teams_collection().update_one(
        {"_id": ObjectId(team_id)}, {"$set": {"usage.executions_count": limit}}
    ))

    resp = client.post("/api/strategy", json={"goal": "x"}, headers=erin)
    assert resp.status_code == 429, resp.text
    assert resp.json()["detail"]["code"] == "USAGE_LIMIT_REACHED"
    assert _usage(client, erin) == limit


def test_login_is_throttled_per_client(app_client):
    client = app_client
    _signup(client, "frank@example.com")
    codes = [
        client.post("/api/auth/login", json={"email": "frank@example.com", "password": "Wrong-Password-1!"}).status_code
        for _ in range(11)
    ]
    assert codes[:10].count(429) == 0 and codes[10] == 429
