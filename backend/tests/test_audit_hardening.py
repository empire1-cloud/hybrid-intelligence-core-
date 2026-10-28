"""
Regression tests for the October 2026 HIC audit fixes.

Every test here exercises the real code path the finding was about. Nothing
in this file makes a network call or needs a running server or MongoDB:
engines get a stub chat client (only ``_create_chat`` is replaced, the same
technique as ``test_engine_output_honesty.py``), and Mongo-backed services
get an in-memory ``mongomock_motor`` collection.

Run:  cd backend && PYTHONPATH=.:<shim> python -m pytest -q tests/test_audit_hardening.py
"""

import asyncio
import importlib
import os
import sys
import types
from datetime import datetime, timedelta, timezone

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

from services import model_policy  # noqa: E402
from services.engine_errors import EngineOutputError  # noqa: E402
from services.model_policy import ModelPolicyError, resolve_engine_model  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# 1. Model policy at the in-process execution boundary
# ─────────────────────────────────────────────────────────────────────────────

ENGINE_SPECS = [
    # (module, class, async method, required kwargs)
    ("services.analysis_engine", "AnalysisEngine", None, None),
    ("services.anime_character_engine", "AnimeCharacterEngine", "generate_character_async", {"concept": "x"}),
    ("services.anime_lore_engine", "AnimeLoreEngine", "generate_lore_async", {"world_concept": "x"}),
    ("services.anime_story_engine", "AnimeStoryEngine", "generate_story_async", {"concept": "x"}),
    ("services.art_direction_engine", "ArtDirectionEngine", "generate_direction_async", {"project": "x"}),
    ("services.blueprint_engine", "BlueprintEngine", "generate_blueprint_async", {"system_description": "x"}),
    ("services.evaluator_engine", "EvaluatorEngine", "evaluate_async", {"subject": "x", "content": "y"}),
    ("services.money_pipeline_engine", "MoneyPipelineEngine", "generate_pipeline_async", {"idea": "x"}),
    ("services.opportunity_mapper", "OpportunityMapperEngine", "map_opportunities_async", {"situation": "x"}),
    ("services.persona_engine", "PersonaEngine", "generate_persona_async", {"audience": "x"}),
    ("services.pipeline_composer", "PipelineComposerEngine", "compose_pipeline_async", {"request": "x"}),
    ("services.pricing_engine", "PricingEngine", "generate_pricing_async", {"product": "x"}),
]


def _engine(module, cls):
    return getattr(importlib.import_module(module), cls)


class _RecordingChat:
    """Captures the provider pair handed to the client."""

    def __init__(self, *a, **k):
        self.provider = None
        self.model = None

    def with_model(self, provider, model):
        self.provider, self.model = provider, model
        return self


@pytest.fixture
def recording_chat(monkeypatch):
    for module, cls, _, _ in ENGINE_SPECS:
        monkeypatch.setattr(importlib.import_module(module), "LlmChat", _RecordingChat)
    return _RecordingChat


@pytest.mark.parametrize("module,cls,_m,_k", ENGINE_SPECS)
@pytest.mark.parametrize("blocked", ["gemini-3-flash", "GEMINI-3-flash", "google-palm", "vertex-ai"])
def test_every_engine_refuses_google_models_in_process(recording_chat, module, cls, _m, _k, blocked):
    with pytest.raises(ModelPolicyError):
        _engine(module, cls)._create_chat(blocked)


@pytest.mark.parametrize("module,cls,_m,_k", ENGINE_SPECS)
def test_every_engine_refuses_unknown_models_instead_of_rerouting(recording_chat, module, cls, _m, _k):
    # Previously MODEL_CONFIG.get(model, default) silently swapped in the default.
    with pytest.raises(ModelPolicyError):
        _engine(module, cls)._create_chat("totally-made-up-model")


@pytest.mark.parametrize("module,cls,_m,_k", ENGINE_SPECS)
def test_every_engine_dispatches_the_approved_model_it_was_asked_for(recording_chat, module, cls, _m, _k):
    chat = _engine(module, cls)._create_chat("gpt-4o")
    # gpt-4o is approved but not in most engines' own MODEL_CONFIG; it must
    # resolve to gpt-4o, not to the engine default.
    assert (chat.provider, chat.model) == ("openai", "gpt-4o")


@pytest.mark.parametrize("module,cls,_m,_k", ENGINE_SPECS)
def test_every_engine_default_is_approved(recording_chat, module, cls, _m, _k):
    chat = _engine(module, cls)._create_chat(None)
    assert chat.provider in {"openai", "anthropic"}


def test_resolver_refuses_a_stale_gemini_provider_pair_even_under_an_approved_name():
    poisoned = {"gpt-5.2": ("gemini", "gemini-3-flash-preview")}
    with pytest.raises(ModelPolicyError):
        resolve_engine_model("gpt-5.2", poisoned)


def test_every_approved_model_has_a_provider_route():
    assert set(model_policy.CANONICAL_PROVIDER_MAP) == set(model_policy.APPROVED_MODELS)


def test_sla113_gemini_image_route_is_blocked_by_default(monkeypatch):
    from fastapi.testclient import TestClient
    import server

    monkeypatch.delenv("SLA113_GEMINI_IMAGE_EXCEPTION", raising=False)
    monkeypatch.setenv("SLA113_OPERATOR_KEY", "k" * 32)
    resp = TestClient(server.app).post(
        "/api/sla113/vision/generate-image",
        json={"prompt": "a boss fish"},
        headers={"X-SLA113-Operator-Key": "k" * 32},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["code"] == "MODEL_POLICY_BLOCKED"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Engines no longer fabricate output on unparseable responses
# ─────────────────────────────────────────────────────────────────────────────

class _StubChat:
    def __init__(self, response):
        self._response = response

    async def send_message(self, *a, **k):
        return self._response


@pytest.mark.parametrize("module,cls,method,kwargs", [s for s in ENGINE_SPECS if s[2]])
def test_engine_raises_instead_of_fabricating(monkeypatch, module, cls, method, kwargs):
    engine = _engine(module, cls)
    monkeypatch.setattr(engine, "_create_chat", classmethod(lambda c, model=None: _StubChat("not json at all")))
    with pytest.raises(EngineOutputError):
        asyncio.run(getattr(engine, method)(**kwargs))


def test_no_engine_still_returns_a_placeholder_on_json_decode_error():
    """Static guard: every `except json.JSONDecodeError:` block in an engine
    must raise, not return. Catches a future engine copying the old pattern."""
    import pathlib
    import re

    services = pathlib.Path(__file__).resolve().parent.parent / "services"
    offenders = []
    for path in services.glob("*.py"):
        lines = path.read_text().splitlines()
        for i, line in enumerate(lines):
            if re.match(r"\s*except\s*\(?\s*json\.JSONDecodeError", line):
                indent = len(line) - len(line.lstrip())
                block = []
                for nxt in lines[i + 1:]:
                    if nxt.strip() and len(nxt) - len(nxt.lstrip()) <= indent:
                        break
                    block.append(nxt.strip())
                body = [b for b in block if b and not b.startswith("#")]
                if body and body[0].startswith("return"):
                    offenders.append(f"{path.name}:{i + 1}")
    assert offenders == []


# ─────────────────────────────────────────────────────────────────────────────
# 3. Secrets never leave the process
# ─────────────────────────────────────────────────────────────────────────────

# Same shape as the real leak, with a fabricated value (never commit a real key).
LEAK = "...generateContent?key=sk-emergent-FAKE0000TEST0000KEY For more information"


def test_redaction_strips_the_exact_leak_shape_found_in_the_repo():
    from services.secret_redaction import redact_secrets

    out = redact_secrets(LEAK)
    assert "sk-emergent" not in out and "FAKE0000TEST0000KEY" not in out


@pytest.mark.parametrize("secret", [
    "Bearer eyJhbGciOiJIUzI1NiJ9.abc.def",
    "sk-ant-api03-abcdefghijklmnop",
    "sk_live_abcdefghijklmnop",
    "whsec_abcdefghijklmnop",
    "hic_abcdefghijklmnopqrstuv",
    "mongodb+srv://user:hunter22@cluster0.example.net/db",
])
def test_redaction_known_credential_shapes(secret):
    from services.secret_redaction import redact_secrets

    out = redact_secrets(f"failure: {secret}")
    assert "[REDACTED]" in out
    assert "hunter22" not in out and "abcdefghijklmnop" not in out


def test_redaction_strips_literal_env_secret_values(monkeypatch):
    from services.secret_redaction import redact_secrets

    monkeypatch.setenv("EMERGENT_LLM_KEY", "plain-looking-value-123456")
    assert "plain-looking-value-123456" not in redact_secrets("got plain-looking-value-123456 back")


def test_http_exception_details_are_redacted_globally():
    from fastapi import HTTPException
    from fastapi.testclient import TestClient
    import server

    path = "/__audit_test_leak"
    if not any(getattr(r, "path", None) == path for r in server.app.routes):
        async def _leaky():
            raise HTTPException(status_code=500, detail=f"Upstream failed: {LEAK}")

        server.app.add_api_route(path, _leaky, methods=["GET"])

    body = TestClient(server.app).get(path).text
    assert "sk-emergent" not in body and "[REDACTED]" in body


def test_error_handler_redacts_provider_errors():
    from services.error_handler import ErrorHandler

    err = ErrorHandler.handle(RuntimeError(LEAK))
    assert "sk-emergent" not in err.message


# ─────────────────────────────────────────────────────────────────────────────
# 4. SLA113 operator guard
# ─────────────────────────────────────────────────────────────────────────────

def _sla113_routes():
    from fastapi.routing import APIRoute
    import server

    for route in server.app.routes:
        if isinstance(route, APIRoute) and route.path.startswith("/api/sla113"):
            yield route


def test_every_sla113_route_carries_the_operator_guard():
    from core.operator_guard import sla113_operator_guard

    def deps(d):
        for sub in d.dependencies:
            yield sub.call
            yield from deps(sub)

    unguarded = [r.path for r in _sla113_routes() if sla113_operator_guard not in set(deps(r.dependant))]
    assert unguarded == []
    assert len(list(_sla113_routes())) >= 70  # the surface the audit found (78)


@pytest.mark.parametrize("method,path", [
    ("post", "/api/sla113/tenants"),
    ("put", "/api/sla113/tenants/T1/credits"),
    ("put", "/api/sla113/tenants/T1/rtp"),
    ("delete", "/api/sla113/projects/P1"),
    ("post", "/api/sla113/terminal"),
    ("post", "/api/sla113/vision/generate-image"),
    ("post", "/api/sla113/worker/toggle"),
    ("get", "/api/sla113/tenants"),
])
def test_anonymous_sla113_writes_and_tenant_reads_are_rejected(monkeypatch, method, path):
    from fastapi.testclient import TestClient
    import server

    monkeypatch.setenv("SLA113_AUTH_MODE", "enforce")
    monkeypatch.setenv("SLA113_OPERATOR_KEY", "k" * 32)
    resp = TestClient(server.app).request(method.upper(), path, json={} if method in ("post", "put") else None)
    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "OPERATOR_REQUIRED"


def test_wrong_or_short_operator_key_is_rejected(monkeypatch):
    from fastapi.testclient import TestClient
    import server

    client = TestClient(server.app)
    monkeypatch.setenv("SLA113_OPERATOR_KEY", "k" * 32)
    assert client.post("/api/sla113/terminal", json={}, headers={"X-SLA113-Operator-Key": "nope"}).status_code == 401
    # A configured key shorter than the minimum never authorises anything.
    monkeypatch.setenv("SLA113_OPERATOR_KEY", "short")
    assert client.post("/api/sla113/terminal", json={}, headers={"X-SLA113-Operator-Key": "short"}).status_code == 401


def _conn(method="GET", path="/api/sla113/lobbies", headers=None, scope_type="http"):
    from starlette.requests import HTTPConnection

    scope = {
        "type": scope_type,
        "method": method,
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()],
        "client": ("203.0.113.9", 1234),
        "server": ("test", 80),
        "scheme": "http",
    }
    return HTTPConnection(scope)


def test_public_reads_and_websockets_stay_open_for_the_arcade(monkeypatch):
    from core.operator_guard import sla113_operator_guard

    monkeypatch.setenv("SLA113_AUTH_MODE", "enforce")
    for path in ("/api/sla113/lobbies", "/api/sla113/sprites", "/api/sla113/live/DPL-ABCDEF12/index.html"):
        assert asyncio.run(sla113_operator_guard(_conn("GET", path))) is None
    assert asyncio.run(sla113_operator_guard(_conn(path="/api/sla113/fish/play/L1", scope_type="websocket"))) is None


def test_valid_operator_key_is_accepted(monkeypatch):
    from core.operator_guard import sla113_operator_guard

    monkeypatch.setenv("SLA113_OPERATOR_KEY", "k" * 32)
    conn = _conn("POST", "/api/sla113/tenants", {"X-SLA113-Operator-Key": "k" * 32})
    assert asyncio.run(sla113_operator_guard(conn)) is None


def test_hic_api_keys_can_never_act_as_operator(monkeypatch):
    from fastapi import HTTPException
    from core.operator_guard import sla113_operator_guard

    monkeypatch.setenv("SLA113_AUTH_MODE", "enforce")
    conn = _conn("POST", "/api/sla113/tenants", {"Authorization": "Bearer hic_abcdefghijklmnop"})
    with pytest.raises(HTTPException) as exc:
        asyncio.run(sla113_operator_guard(conn))
    assert exc.value.status_code == 401


def test_showcase_demo_deploy_is_public_but_rate_limited(monkeypatch):
    from fastapi import HTTPException
    from core import operator_guard
    from core.rate_limit import reset_rate_limits

    reset_rate_limits()
    monkeypatch.setattr(operator_guard, "PUBLIC_WRITE_LIMIT", 2)
    conn = lambda: _conn("POST", "/api/sla113/lobbies/LBY-1/deploy", {"X-Real-IP": "198.51.100.7"})
    assert asyncio.run(operator_guard.sla113_operator_guard(conn())) is None
    assert asyncio.run(operator_guard.sla113_operator_guard(conn())) is None
    with pytest.raises(HTTPException) as exc:
        asyncio.run(operator_guard.sla113_operator_guard(conn()))
    assert exc.value.status_code == 429
    reset_rate_limits()


def test_audit_mode_logs_but_does_not_block(monkeypatch):
    from core.operator_guard import sla113_operator_guard

    monkeypatch.setenv("SLA113_AUTH_MODE", "audit")
    assert asyncio.run(sla113_operator_guard(_conn("POST", "/api/sla113/tenants"))) is None


def test_ecosystem_patch_requires_operator(monkeypatch):
    from fastapi.testclient import TestClient
    import server

    monkeypatch.setenv("SLA113_AUTH_MODE", "enforce")
    resp = TestClient(server.app).patch("/api/empire1/ecosystem/hic", json={"production_url": "https://evil.example"})
    assert resp.status_code == 401


def test_live_file_server_rejects_traversal(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    import server
    from routers import sla113

    deploy = tmp_path / "DPL-ABCDEF12"
    deploy.mkdir()
    (deploy / "index.html").write_text("ok")
    (tmp_path / "DPL-ABCDEF12_evil").mkdir()
    (tmp_path / "DPL-ABCDEF12_evil" / "x.html").write_text("secret")
    monkeypatch.setattr(sla113, "SLA113_DEPLOY_ROOT", str(tmp_path))

    client = TestClient(server.app)
    assert client.get("/api/sla113/live/DPL-ABCDEF12/index.html").text == "ok"
    # Encoded so the client does not normalise it away; the handler receives
    # file_path="../DPL-ABCDEF12_evil/x.html". The old str.startswith check
    # against the deploys root accepted this.
    resp = client.get("/api/sla113/live/DPL-ABCDEF12/..%2FDPL-ABCDEF12_evil%2Fx.html")
    assert resp.status_code == 403 and "secret" not in resp.text


@pytest.mark.parametrize("url", [
    "http://example.com/a.png",
    "https://localhost/a.png",
    "https://127.0.0.1/a.png",
    "https://10.0.0.5/a.png",
    "https://169.254.169.254/latest/meta-data",
    "https://[::1]/a.png",
    "https://user:pw@93.184.216.34/a.png",
    "https://metadata.internal/a.png",
])
def test_sprite_proxy_refuses_non_public_targets(url):
    from core.url_safety import UnsafeURLError, assert_public_https_url

    with pytest.raises(UnsafeURLError):
        assert_public_https_url(url)


def test_sprite_proxy_allows_public_literal_ip():
    from core.url_safety import assert_public_https_url

    assert_public_https_url("https://93.184.216.34/sprite.png")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Security configuration
# ─────────────────────────────────────────────────────────────────────────────

def test_jwt_secret_fails_closed_in_production(monkeypatch):
    from core import security

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        security._load_jwt_secret()
    monkeypatch.setenv("JWT_SECRET_KEY", "too-short")
    with pytest.raises(RuntimeError):
        security._load_jwt_secret()
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 40)
    assert security._load_jwt_secret() == "x" * 40


def test_jwt_secret_dev_fallback_still_works(monkeypatch):
    from core import security

    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    assert len(security._load_jwt_secret()) >= 32


def test_cors_never_pairs_wildcard_with_credentials(monkeypatch):
    from core.cors_config import resolve_cors_settings

    for raw in ("", "*", "https://a.example,*"):
        monkeypatch.setenv("CORS_ORIGINS", raw)
        settings = resolve_cors_settings()
        assert settings["allow_origins"] == ["*"] and settings["allow_credentials"] is False

    monkeypatch.setenv("CORS_ORIGINS", "https://app.example.com/, https://admin.example.com")
    settings = resolve_cors_settings()
    assert settings["allow_origins"] == ["https://app.example.com", "https://admin.example.com"]
    assert settings["allow_credentials"] is True


# ─────────────────────────────────────────────────────────────────────────────
# 6. Billing webhook
# ─────────────────────────────────────────────────────────────────────────────

def _mongo_collection(name):
    from mongomock_motor import AsyncMongoMockClient

    return AsyncMongoMockClient()["hic_test"][name]


def test_webhook_rejects_unsigned_events_when_secret_missing(monkeypatch):
    from services import billing_service

    monkeypatch.setattr(billing_service, "STRIPE_AVAILABLE", True)
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    forged = b'{"id":"evt_1","type":"checkout.session.completed","data":{"object":{"metadata":{"team_id":"x","plan":"pro"}}}}'
    with pytest.raises(billing_service.BillingError) as exc:
        asyncio.run(billing_service.handle_webhook_event(forged, ""))
    assert exc.value.status_code == 503


def test_webhook_applies_each_event_once(monkeypatch):
    from services import billing_service

    events = _mongo_collection("billing_events")
    dispatched = []

    async def _dispatch(event_type, data):
        dispatched.append(event_type)

    monkeypatch.setattr(billing_service, "STRIPE_AVAILABLE", True)
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setattr(billing_service, "billing_events_collection", lambda: events)
    monkeypatch.setattr(billing_service, "_dispatch_billing_event", _dispatch)
    monkeypatch.setattr(
        billing_service.stripe.Webhook, "construct_event",
        staticmethod(lambda payload, sig, secret: {"id": "evt_42", "type": "invoice.paid", "data": {"object": {}}}),
    )

    first = asyncio.run(billing_service.handle_webhook_event(b"{}", "sig"))
    second = asyncio.run(billing_service.handle_webhook_event(b"{}", "sig"))
    assert dispatched == ["invoice.paid"]
    assert first.get("duplicate") is None and second["duplicate"] is True


def test_checkout_redirects_are_limited_to_the_app_origin(monkeypatch):
    from services import billing_service

    monkeypatch.setattr(billing_service, "APP_URL", "https://app.example.com")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    default = "https://app.example.com/billing"
    assert billing_service._same_origin_or_default("https://evil.example/phish", default) == default
    assert billing_service._same_origin_or_default("https://app.example.com/billing?ok=1", default).endswith("ok=1")
    assert billing_service._same_origin_or_default(None, default) == default


# ─────────────────────────────────────────────────────────────────────────────
# 7. Usage metering
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def usage_env(monkeypatch):
    from bson import ObjectId
    from services import usage_service

    teams = _mongo_collection("teams")
    monkeypatch.setattr(usage_service, "teams_collection", lambda: teams)
    monkeypatch.setattr(
        usage_service, "get_plan_limits",
        lambda plan: {"executions_per_month": 5 if plan == "free" else -1},
    )
    team_id = ObjectId()
    asyncio.run(teams.insert_one({"_id": team_id, "billing": {"plan": "free"}, "usage": {"executions_count": 0}}))
    return usage_service, teams, str(team_id), team_id


def test_concurrent_reservations_never_exceed_the_plan(usage_env):
    usage_service, teams, team_id, oid = usage_env

    async def attempt():
        try:
            return await usage_service.reserve_execution(team_id)
        except usage_service.UsageLimitError:
            return "limited"

    async def burst():
        return await asyncio.gather(*[attempt() for _ in range(25)])

    results = asyncio.run(burst())
    assert results.count(True) == 5 and results.count("limited") == 20
    doc = asyncio.run(teams.find_one({"_id": oid}))
    assert doc["usage"]["executions_count"] == 5


def test_failed_execution_releases_its_slot(usage_env):
    usage_service, teams, team_id, oid = usage_env
    assert asyncio.run(usage_service.reserve_execution(team_id)) is True
    asyncio.run(usage_service.release_execution(team_id))
    asyncio.run(usage_service.release_execution(team_id))  # never below zero
    assert asyncio.run(teams.find_one({"_id": oid}))["usage"]["executions_count"] == 0


def test_team_without_period_start_gets_a_monthly_reset(usage_env):
    usage_service, teams, team_id, oid = usage_env
    asyncio.run(teams.update_one({"_id": oid}, {"$set": {"usage.executions_count": 5}}))
    # Previously: period_start was never written, so this team stayed at 5/5 forever.
    assert asyncio.run(usage_service.reserve_execution(team_id)) is True
    doc = asyncio.run(teams.find_one({"_id": oid}))
    assert doc["usage"]["executions_count"] == 1 and doc["usage"].get("period_start") is not None


def test_previous_month_usage_rolls_over(usage_env):
    usage_service, teams, team_id, oid = usage_env
    last_month = datetime.now(timezone.utc).replace(day=1) - timedelta(days=3)
    asyncio.run(teams.update_one({"_id": oid}, {"$set": {"usage.executions_count": 5, "usage.period_start": last_month}}))
    assert asyncio.run(usage_service.reserve_execution(team_id)) is True


def test_limit_reached_is_a_429_not_a_500(monkeypatch):
    from fastapi import HTTPException
    from core import engine_context
    from services.usage_service import UsageLimitError

    async def _limited(team_id, amount=1):
        raise UsageLimitError("limit", "executions", 5, 5)

    class _Ctx:
        team_id = "t"
        actor_type = "user"

        def require_read(self):
            pass

        def require_write(self):
            pass

    async def _ctx(request, credentials):
        return _Ctx()

    monkeypatch.setattr(engine_context, "reserve_execution", _limited)
    monkeypatch.setattr(engine_context, "get_engine_context", _ctx)

    class _Req:
        method = "POST"

        class url:
            path = "/api/strategy"

        class state:
            pass

    with pytest.raises(HTTPException) as exc:
        asyncio.run(engine_context.enforce_engine_subscription(_Req(), None))
    assert exc.value.status_code == 429
    assert exc.value.detail["code"] == "USAGE_LIMIT_REACHED"


def test_increment_with_nothing_to_count_does_not_send_an_empty_inc(usage_env):
    usage_service, teams, team_id, oid = usage_env
    asyncio.run(usage_service.increment_usage(team_id, executions=0, api_calls=0))


# ─────────────────────────────────────────────────────────────────────────────
# 8. Tenant isolation of the in-memory core log
# ─────────────────────────────────────────────────────────────────────────────

def test_core_log_is_team_scoped():
    from services.hybrid_core import CURRENT_TEAM_ID, HybridIntelligenceCore

    core = HybridIntelligenceCore()
    CURRENT_TEAM_ID.set("team-a")
    core._log_execution("team A private prompt", None, {}, success=True)
    CURRENT_TEAM_ID.set("team-b")
    core._log_execution("team B private prompt", None, {}, success=True)
    CURRENT_TEAM_ID.set(None)

    a = core.get_execution_log(50, team_id="team-a")
    assert [e["prompt_preview"] for e in a] == ["team A private prompt"]
    assert core.get_execution_log(50, team_id="team-c") == []


# ─────────────────────────────────────────────────────────────────────────────
# 9. Analytics never invents numbers
# ─────────────────────────────────────────────────────────────────────────────

def _fresh_analytics(monkeypatch, logs):
    from routers.engines import analytics

    analytics._cache.clear()
    analytics._cache_ttl.clear()

    class _Logger:
        def __init__(self):
            self.logs = logs

        def get_stats(self):
            return {"engines": {}, "total_executions": len(logs)}

    monkeypatch.setattr(analytics, "get_logger", lambda: _Logger())
    return analytics


def test_system_health_without_psutil_reports_null_not_random(monkeypatch):
    analytics = _fresh_analytics(monkeypatch, [])
    monkeypatch.setattr(analytics, "PSUTIL_AVAILABLE", False)
    result = asyncio.run(analytics.get_system_health())
    assert result.cpu_usage is None and result.memory_usage is None and result.status == "unknown"
    assert analytics.get_system_health_data()["cpu_usage"] is None


def test_confidence_trends_are_empty_without_data_and_deterministic_with_it(monkeypatch):
    from services.execution_logger import ExecutionLog

    analytics = _fresh_analytics(monkeypatch, [])
    assert asyncio.run(analytics.get_confidence_trends()) == []

    now = datetime.now(timezone.utc).isoformat()
    logs = [
        ExecutionLog(id="1", timestamp=now, engine="strategy_engine", endpoint="/x", method="POST", source="api",
                     input_data={}, output_data={"metadata": {"confidence": 0.8}}, status="success", duration_ms=10),
        ExecutionLog(id="2", timestamp=now, engine="strategy_engine", endpoint="/x", method="POST", source="api",
                     input_data={}, output_data={}, status="success", duration_ms=10),
    ]
    analytics = _fresh_analytics(monkeypatch, logs)
    first = asyncio.run(analytics.get_confidence_trends())
    analytics._cache.clear()
    second = asyncio.run(analytics.get_confidence_trends())
    values = [p.value for p in first[0].data_points]
    assert values == [p.value for p in second[0].data_points]  # no random noise
    assert values[-1] == 0.8 and all(v is None for v in values[:-2])


def test_drift_without_enough_data_is_unknown_not_green(monkeypatch):
    from services.execution_logger import ExecutionLog

    analytics = _fresh_analytics(monkeypatch, [])
    assert asyncio.run(analytics.get_drift_status()) == []

    now = datetime.now(timezone.utc).isoformat()
    analytics = _fresh_analytics(monkeypatch, [
        ExecutionLog(id="1", timestamp=now, engine="pricing_engine", endpoint="/x", method="POST", source="api",
                     input_data={}, status="success", duration_ms=10),
    ])
    (alert,) = asyncio.run(analytics.get_drift_status())
    assert alert.status == "unknown"


def test_pipeline_graph_queue_length_is_not_random(monkeypatch):
    analytics = _fresh_analytics(monkeypatch, [])
    assert asyncio.run(analytics.get_pipeline_graph()).queue_length is None


def test_model_comparison_is_labelled_static_and_gemini_unavailable():
    from routers.engines import analytics

    data = asyncio.run(analytics.get_model_comparison())
    assert data["measured"] is False
    gemini = [m for m in data["models"] if m["provider"] == "Google"]
    assert gemini and all(m["available"] is False for m in gemini)


def test_reservation_is_released_when_the_engine_raises(monkeypatch):
    """Codex review on PR #18: if a route lets an exception escape,
    BaseHTTPMiddleware's call_next re-raises, so a release placed only on the
    >=400 response path never runs and the reserved slot leaks."""
    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient
    from middleware import subscription_usage_middleware as mw

    released = []

    async def _release(team_id, amount=1):
        released.append((team_id, amount))

    monkeypatch.setattr(mw, "release_execution", _release)

    class _Ctx:
        team_id = "team-x"
        actor_type = "user"

    app = FastAPI()
    app.add_middleware(mw.SubscriptionUsageMiddleware)

    @app.post("/boom")
    async def _boom(request: Request):
        request.state.engine_context = _Ctx()
        request.state.hic_execution_pending = True
        request.state.hic_execution_reserved = True
        raise RuntimeError("engine blew up")

    resp = TestClient(app, raise_server_exceptions=False).post("/boom")
    assert resp.status_code == 500
    assert released == [("team-x", 1)]
