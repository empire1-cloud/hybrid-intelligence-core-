"""
Engine output honesty tests -- pass 2's crown-jewel fix.

Pass 1 found that `strategy_engine.py`, `plan_builder.py` and
`analysis_engine.py` each fell back to a hardcoded, fabricated placeholder
dict on `json.JSONDecodeError` -- a founder would see invented content
rendered as a completed strategy/plan/analysis. `test_canon_contract.py` and
`test_canon_orchestrator.py` proved the canon-layer *mapper* detects and
refuses that shape. This file proves the fix at its actual source: these
tests exercise the REAL `StrategyEngine` / `PlanBuilderEngine` /
`AnalysisEngine` parsing logic -- only `_create_chat` is replaced, so
`.send_message()`'s return value is the only thing under this test's
control -- and confirm each one now raises `EngineOutputError` instead of
returning fabricated JSON. This is the same class of proof
`test_startup_copilot_contract.py::test_unparseable_response_raises_instead_of_fabricating`
already established for the 12 founder skills.

`_create_chat` is monkeypatched per test rather than stubbing
`emergentintegrations.llm.chat` at module scope: several sibling test files
in this suite also stub that module at import time, and pytest.ini pins 2
xdist workers that each run multiple test files in one process, so
`sys.modules["emergentintegrations.llm.chat"]` can already be bound to a
different (weaker) fake by the time this file's own module-level stub would
run, if another file happened to import an engine module first on the same
worker. Patching `_create_chat` directly on each engine class sidesteps that
ordering entirely -- no live LLM call is made either way.
"""

import asyncio
import sys
import types

import pytest


def _ensure_emergentintegrations_importable():
    """Only needed so `from emergentintegrations.llm.chat import ...` in the
    engine modules doesn't raise ModuleNotFoundError on first import in a
    fresh worker. The actual chat behavior in this file comes from patching
    `_create_chat`, not from whatever ends up bound here.
    """
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

from services.analysis_engine import AnalysisEngine  # noqa: E402
from services.engine_errors import EngineOutputError  # noqa: E402
from services.plan_builder import PlanBuilderEngine  # noqa: E402
from services.strategy_engine import StrategyEngine  # noqa: E402


NON_JSON_RESPONSE = "Sorry, I can't help with that right now."


class _StubChat:
    """Controllable fake chat client. `response` is set per-test."""

    def __init__(self, response):
        self._response = response

    async def send_message(self, *a, **k):
        return self._response


def _patch_chat(monkeypatch, engine_cls, response):
    monkeypatch.setattr(engine_cls, "_create_chat", classmethod(lambda cls, model=None: _StubChat(response)))


# ---------------------------------------------------------------------------
# The fix: unparseable output raises, it is not fabricated into a fake result
# ---------------------------------------------------------------------------
def test_strategy_engine_raises_on_unparseable_response(monkeypatch):
    _patch_chat(monkeypatch, StrategyEngine, NON_JSON_RESPONSE)
    with pytest.raises(EngineOutputError) as exc_info:
        asyncio.run(StrategyEngine.generate_async(model="gpt-5.2", goal="Grow revenue"))
    assert exc_info.value.response_text == NON_JSON_RESPONSE


def test_plan_builder_engine_raises_on_unparseable_response(monkeypatch):
    _patch_chat(monkeypatch, PlanBuilderEngine, NON_JSON_RESPONSE)
    with pytest.raises(EngineOutputError) as exc_info:
        asyncio.run(PlanBuilderEngine.build_plan_async(goal="Ship the launch", model="gpt-5.2"))
    assert exc_info.value.response_text == NON_JSON_RESPONSE


def test_analysis_engine_raises_on_unparseable_response(monkeypatch):
    _patch_chat(monkeypatch, AnalysisEngine, NON_JSON_RESPONSE)
    with pytest.raises(EngineOutputError) as exc_info:
        asyncio.run(AnalysisEngine.analyze_async(subject="Our retention curve", model="claude-sonnet-4.5"))
    assert exc_info.value.response_text == NON_JSON_RESPONSE


@pytest.mark.parametrize(
    "malformed",
    [
        "",
        "Sure! Here's my analysis: {not valid json",
        '{"summary": "truncated mid-object"',
        "Just prose, no JSON at all.",
    ],
)
def test_strategy_engine_raises_on_every_malformed_shape(monkeypatch, malformed):
    _patch_chat(monkeypatch, StrategyEngine, malformed)
    with pytest.raises(EngineOutputError):
        asyncio.run(StrategyEngine.generate_async(model="gpt-5.2", goal="x"))


# ---------------------------------------------------------------------------
# Regression guard: the happy path must still work -- this is a parse-failure
# fix, not a behavior change for well-formed responses.
# ---------------------------------------------------------------------------
def test_strategy_engine_still_parses_well_formed_json(monkeypatch):
    _patch_chat(
        monkeypatch, StrategyEngine,
        '{"summary": "s", "steps": ["a"], "risks": [], "resources": [], "next_action": "b"}',
    )
    result = asyncio.run(StrategyEngine.generate_async(model="gpt-5.2", goal="x"))
    assert result == {"summary": "s", "steps": ["a"], "risks": [], "resources": [], "next_action": "b"}


def test_plan_builder_engine_still_parses_well_formed_json(monkeypatch):
    _patch_chat(
        monkeypatch, PlanBuilderEngine,
        '{"objective": "o", "phases": [], "milestones": [], "critical_path": [], "first_24_hours": []}',
    )
    result = asyncio.run(PlanBuilderEngine.build_plan_async(goal="x", model="gpt-5.2"))
    assert result["objective"] == "o"


def test_analysis_engine_still_parses_well_formed_json(monkeypatch):
    _patch_chat(
        monkeypatch, AnalysisEngine,
        '{"overview": "o", "strengths": [], "weaknesses": [], "opportunities": [], '
        '"threats": [], "key_insights": [], "recommended_focus": "f"}',
    )
    result = asyncio.run(AnalysisEngine.analyze_async(subject="x", model="claude-sonnet-4.5"))
    assert result["overview"] == "o"


def test_strategy_engine_still_unwraps_markdown_fenced_json(monkeypatch):
    _patch_chat(
        monkeypatch, StrategyEngine,
        '```json\n{"summary": "s", "steps": [], "risks": [], "resources": [], "next_action": "n"}\n```',
    )
    result = asyncio.run(StrategyEngine.generate_async(model="gpt-5.2", goal="x"))
    assert result["summary"] == "s"


def test_engines_use_no_bare_except():
    """A bare except also swallows KeyboardInterrupt and masks real failures.

    Same guard startup_copilot_engines.py already carries
    (test_startup_copilot_contract.py::test_engines_use_no_bare_except),
    applied to the three engines fixed in this pass.
    """
    from pathlib import Path

    backend = Path(__file__).resolve().parents[1]
    for filename in ("services/strategy_engine.py", "services/plan_builder.py", "services/analysis_engine.py"):
        source = (backend / filename).read_text()
        offenders = [i + 1 for i, line in enumerate(source.splitlines()) if line.strip() == "except:"]
        assert not offenders, f"bare except in {filename} on lines {offenders}"
