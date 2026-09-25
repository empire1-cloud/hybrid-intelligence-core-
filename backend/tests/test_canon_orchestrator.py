"""
Canon Orchestrator tests.

`services/hybrid_core.py::HybridIntelligenceCore.execute()` only ever calls
StrategyEngine or PlanBuilderEngine, regardless of task type -- its own
ENGINE_MAP is declared and never read. Pass 1 proved Analysis was reachable;
pass 2 adds Opportunity Mapper, Evaluator, Pricing and Persona (see
`services/canon_routing.py`). These tests also prove a simulated
primary-model failure produces a real fallback (not a silent single point of
failure), and that a fabricated parse-failure response is refused rather
than persisted as a canon output -- as defense-in-depth now that pass 2 made
Strategy/Plan/Analysis raise `EngineOutputError` at the source instead of
producing that shape at all (see `test_engine_output_honesty.py` for the
source-level proof).

No live LLM call is made anywhere in this file: `emergentintegrations` is
stubbed (same technique as `test_startup_copilot_contract.py::_stub_llm`) and
every engine classmethod that would call it is monkeypatched.

Task types are passed as the plain string keys from
`services.canon_routing.CANON_ENGINE_KEYS` -- pass 1 typed this parameter as
`services.hybrid_core.TaskType`; pass 2 decoupled the canon layer from that
enum entirely (`canon_orchestrator.py` no longer imports `hybrid_core` at
all), since TaskType's own categories were too narrow for the wider engine
set this layer now reaches.
"""

import asyncio
import sys
import types

import pytest


def _stub_llm():
    for name in ("emergentintegrations", "emergentintegrations.llm", "emergentintegrations.llm.chat"):
        sys.modules.setdefault(name, types.ModuleType(name))
    chat = sys.modules["emergentintegrations.llm.chat"]
    if not hasattr(chat, "LlmChat"):
        class _Stub:
            def __init__(self, *a, **k):
                pass

            def with_model(self, *a, **k):
                return self

        chat.LlmChat = _Stub
        chat.UserMessage = _Stub


_stub_llm()

from services.analysis_engine import AnalysisEngine  # noqa: E402
from services.canon_contract import CanonContractError  # noqa: E402
from services.canon_orchestrator import CanonicalOrchestrator  # noqa: E402
from services.evaluator_engine import EvaluatorEngine  # noqa: E402
from services.opportunity_mapper import OpportunityMapperEngine  # noqa: E402
from services.persona_engine import PersonaEngine  # noqa: E402
from services.plan_builder import PlanBuilderEngine  # noqa: E402
from services.pricing_engine import PricingEngine  # noqa: E402
from services.strategy_engine import StrategyEngine  # noqa: E402


STRATEGY_OK = {
    "summary": "Fix onboarding, not acquisition.",
    "steps": ["Cut signup fields"],
    "risks": [],
    "resources": [],
    "next_action": "Ship the shorter form.",
}

ANALYSIS_OK = {
    "overview": "Retention is strong, acquisition is unmodeled.",
    "strengths": [],
    "weaknesses": [],
    "opportunities": [],
    "threats": [],
    "key_insights": ["CAC is unmodeled"],
    "recommended_focus": "Model CAC before scaling spend.",
}

OPPORTUNITY_OK = {
    "context_summary": "A creator marketplace with strong supply, weak demand.",
    "opportunities": [{"name": "Demand-side referral loop", "impact": "high"}],
    "top_3_opportunities": ["Demand-side referral loop"],
    "recommended_next_move": "Ship a referral loop for buyers.",
}

EVALUATOR_OK = {
    "subject": "Referral loop idea",
    "criteria": [{"name": "impact", "score": 8, "weight": 0.5, "rationale": "x"}],
    "weighted_score": 8.0,
    "strengths": ["Clear mechanism"],
    "weaknesses": [],
    "improvement_suggestions": ["Add a double-sided incentive"],
    "go_no_go": "go",
}

PRICING_OK = {
    "offer_summary": "Creator marketplace subscription",
    "target_segments": ["Indie creators"],
    "pricing_model": "subscription",
    "tiers": [{"name": "Starter", "price": "$19/month"}],
    "monetization_risks": [],
    "expansion_opportunities": [],
    "recommended_entry_tier": "Starter",
}

PERSONA_OK = {
    "name": "Dana the Indie Creator",
    "role": "Solo newsletter writer",
    "background": "Runs a niche newsletter and wants to monetize directly.",
    "goals": ["Own the audience relationship"],
    "pains": ["Platform fees eat margin"],
    "triggers": ["Hits a growth plateau on a rented platform"],
    "buying_criteria": ["Low fees"],
    "objections": ["Migration effort"],
    "preferred_channels": ["Email"],
    "preferred_messaging": ["Keep more of what you earn"],
}


def test_analysis_task_actually_reaches_analysis_engine(monkeypatch):
    """Regression guard for the dead ENGINE_MAP: analysis prompts must reach AnalysisEngine."""
    called_with = {}

    async def fake_analyze_async(subject, context=None, model=None, **kwargs):
        called_with["subject"] = subject
        called_with["model"] = model
        return ANALYSIS_OK

    monkeypatch.setattr(AnalysisEngine, "analyze_async", fake_analyze_async)

    orchestrator = CanonicalOrchestrator()
    result = asyncio.run(
        orchestrator.execute(prompt="Analyze our retention curve", task_type="analysis")
    )

    assert result.success is True
    assert called_with["subject"] == "Analyze our retention curve"
    assert result.four_part["source_engine"] == "analysis_engine"
    assert result.four_part["leverage_point"] == ANALYSIS_OK["recommended_focus"]
    assert result.metadata["task_type"] == "analysis"


def test_plan_task_reaches_plan_builder_engine(monkeypatch):
    plan_output = {
        "objective": "Ship the form",
        "phases": [],
        "milestones": [],
        "critical_path": ["Build it"],
        "first_24_hours": ["Draft schema"],
    }

    async def fake_build_plan_async(goal, strategy=None, context=None, model=None):
        return plan_output

    monkeypatch.setattr(PlanBuilderEngine, "build_plan_async", fake_build_plan_async)

    orchestrator = CanonicalOrchestrator()
    result = asyncio.run(orchestrator.execute(prompt="Build a rollout plan", task_type="plan"))

    assert result.success is True
    assert result.four_part["source_engine"] == "plan_builder_engine"
    assert result.four_part["leverage_point"] == "Build it"


def test_general_task_falls_back_to_strategy_engine(monkeypatch):
    async def fake_generate_async(model, goal, context=None, tone="direct"):
        return STRATEGY_OK

    monkeypatch.setattr(StrategyEngine, "generate_async", fake_generate_async)

    orchestrator = CanonicalOrchestrator()
    result = asyncio.run(orchestrator.execute(prompt="What is our best move?", task_type="general"))

    assert result.success is True
    assert result.four_part["source_engine"] == "strategy_engine"


def test_orchestrator_falls_back_when_primary_model_fails(monkeypatch):
    """The first approved model in the chain fails; the orchestrator must retry, not just error out."""
    attempts = []

    async def flaky_generate_async(model, goal, context=None, tone="direct"):
        attempts.append(model)
        if model == "gpt-5.2":
            raise RuntimeError("simulated provider timeout")
        return STRATEGY_OK

    monkeypatch.setattr(StrategyEngine, "generate_async", flaky_generate_async)

    orchestrator = CanonicalOrchestrator()
    result = asyncio.run(
        orchestrator.execute(prompt="What is our best move?", task_type="strategy", force_model="gpt-5.2")
    )

    assert result.success is True
    assert len(attempts) >= 2
    assert attempts[0] == "gpt-5.2"
    assert result.metadata["fallback_used"] is True
    assert result.metadata["model_used"] != "gpt-5.2"


def test_orchestrator_refuses_to_canonize_a_fabricated_fallback(monkeypatch):
    """Defense-in-depth: even if an engine call returns the old fabricated
    shape directly (StrategyEngine itself no longer produces it -- see
    test_engine_output_honesty.py -- but this proves the mapper still
    refuses it if one ever did), it must not be presented as a real canon
    output."""

    async def fabricating_generate_async(model, goal, context=None, tone="direct"):
        return {
            "summary": "raw text",
            "steps": ["Review the generated content and extract actionable steps"],
            "risks": ["Response was not in expected JSON format"],
            "resources": [],
            "next_action": "Retry with a more specific goal",
        }

    monkeypatch.setattr(StrategyEngine, "generate_async", fabricating_generate_async)

    orchestrator = CanonicalOrchestrator()
    result = asyncio.run(orchestrator.execute(prompt="What is our best move?", task_type="strategy"))

    assert result.success is False
    assert result.error["type"] == "canon_error"


def test_orchestrator_never_dispatches_a_blocked_model(monkeypatch):
    """force_model of a Google model must fail closed before any engine call happens."""

    async def should_not_be_called(*args, **kwargs):
        raise AssertionError("engine must not be called with a blocked model")

    monkeypatch.setattr(StrategyEngine, "generate_async", should_not_be_called)

    orchestrator = CanonicalOrchestrator()
    result = asyncio.run(
        orchestrator.execute(prompt="x", task_type="general", force_model="gemini-3-flash")
    )

    assert result.success is False


# ---------------------------------------------------------------------------
# Pass 2: newly-wired engines. Each of these was previously unreachable from
# any orchestrator -- HybridIntelligenceCore's ENGINE_MAP never read these
# entries, and CanonicalOrchestrator (pass 1) only reached Strategy/Plan/Analysis.
# ---------------------------------------------------------------------------
def test_opportunity_task_reaches_opportunity_mapper_engine(monkeypatch):
    called_with = {}

    async def fake_map_opportunities_async(situation, context=None, model=None, **kwargs):
        called_with["situation"] = situation
        return OPPORTUNITY_OK

    monkeypatch.setattr(OpportunityMapperEngine, "map_opportunities_async", fake_map_opportunities_async)

    orchestrator = CanonicalOrchestrator()
    result = asyncio.run(
        orchestrator.execute(prompt="Where are the whitespace opportunities here?", task_type="opportunity")
    )

    assert result.success is True
    assert called_with["situation"] == "Where are the whitespace opportunities here?"
    assert result.four_part["source_engine"] == "opportunity_mapper_engine"
    assert result.four_part["leverage_point"] == OPPORTUNITY_OK["recommended_next_move"]


def test_evaluator_task_reaches_evaluator_engine(monkeypatch):
    async def fake_evaluate_async(subject, content, criteria=None, criteria_preset=None, context=None, model=None):
        return EVALUATOR_OK

    monkeypatch.setattr(EvaluatorEngine, "evaluate_async", fake_evaluate_async)

    orchestrator = CanonicalOrchestrator()
    result = asyncio.run(orchestrator.execute(prompt="Score this idea for me", task_type="evaluator"))

    assert result.success is True
    assert result.four_part["source_engine"] == "evaluator_engine"
    assert result.four_part["leverage_point"] == EVALUATOR_OK["improvement_suggestions"][0]


def test_pricing_task_reaches_pricing_engine(monkeypatch):
    async def fake_generate_pricing_async(product, description=None, target_market=None, competitors=None,
                                           pricing_model=None, constraints=None, model=None):
        return PRICING_OK

    monkeypatch.setattr(PricingEngine, "generate_pricing_async", fake_generate_pricing_async)

    orchestrator = CanonicalOrchestrator()
    result = asyncio.run(orchestrator.execute(prompt="What should I charge for this?", task_type="pricing"))

    assert result.success is True
    assert result.four_part["source_engine"] == "pricing_engine"
    assert "Starter" in result.four_part["leverage_point"]


def test_persona_task_reaches_persona_engine(monkeypatch):
    async def fake_generate_persona_async(audience, context=None, product=None, industry=None, model=None):
        return PERSONA_OK

    monkeypatch.setattr(PersonaEngine, "generate_persona_async", fake_generate_persona_async)

    orchestrator = CanonicalOrchestrator()
    result = asyncio.run(
        orchestrator.execute(prompt="Build me a buyer persona for indie creators", task_type="persona")
    )

    assert result.success is True
    assert result.four_part["source_engine"] == "persona_engine"
    assert result.four_part["leverage_point"] == PERSONA_OK["triggers"][0]


def test_auto_classification_routes_pricing_prompt_to_pricing_engine(monkeypatch):
    """No task_type given -- classify_canon_task must pick the right engine."""

    async def fake_generate_pricing_async(product, description=None, target_market=None, competitors=None,
                                           pricing_model=None, constraints=None, model=None):
        return PRICING_OK

    monkeypatch.setattr(PricingEngine, "generate_pricing_async", fake_generate_pricing_async)

    orchestrator = CanonicalOrchestrator()
    result = asyncio.run(
        orchestrator.execute(prompt="How much should I charge for a subscription tier?")
    )

    assert result.success is True
    assert result.four_part["source_engine"] == "pricing_engine"
    assert result.metadata["task_type"] == "pricing"
