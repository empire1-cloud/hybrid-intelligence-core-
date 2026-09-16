"""
Canon Contract mapper tests.

Verifies the four-part mapping (Core Insight -> System Blueprint -> Leverage
Point -> Executable Output) for each supported source engine, and that a
detected fabricated parse-failure fallback raises `CanonContractError` instead
of being canonized as real insight -- the same protection
`test_startup_copilot_contract.py::test_unparseable_response_raises_instead_of_fabricating`
already proves for the 12 founder skills, extended here to Strategy, Plan
Builder and Analysis without touching those engine files.
"""

import pytest

from models.canon_contract import FourPartOutput
from services.canon_contract import CanonContractError, FourPartContractMapper


# ---------------------------------------------------------------------------
# Happy path: real engine output maps onto the four-part contract
# ---------------------------------------------------------------------------

def test_from_strategy_maps_all_four_parts():
    strategy_output = {
        "summary": "The bottleneck is onboarding drop-off, not demand.",
        "steps": ["Instrument the funnel", "Cut signup fields from 12 to 3"],
        "risks": ["Instrumentation takes a day to trust"],
        "resources": ["Analytics access"],
        "next_action": "Cut the signup form to 3 fields.",
    }

    result = FourPartContractMapper.from_strategy(strategy_output, model_used="claude-sonnet-4.5")

    assert isinstance(result, FourPartOutput)
    assert result.core_insight == strategy_output["summary"]
    assert result.system_blueprint["steps"] == strategy_output["steps"]
    assert result.leverage_point == strategy_output["next_action"]
    assert result.executable_output == strategy_output["steps"]
    assert result.source_engine == "strategy_engine"
    assert result.model_used == "claude-sonnet-4.5"
    assert result.raw == strategy_output


def test_from_plan_maps_all_four_parts():
    plan_output = {
        "objective": "Ship the 3-field signup form.",
        "phases": [{"name": "Build", "duration": "2 days", "tasks": []}],
        "milestones": ["Form live in prod"],
        "critical_path": ["Frontend build", "QA pass"],
        "first_24_hours": ["Draft the new form schema"],
    }

    result = FourPartContractMapper.from_plan(plan_output, model_used="gpt-5.2")

    assert result.core_insight == plan_output["objective"]
    assert result.system_blueprint["phases"] == plan_output["phases"]
    assert result.leverage_point == plan_output["critical_path"][0]
    assert result.executable_output == plan_output["first_24_hours"]
    assert result.source_engine == "plan_builder_engine"


def test_from_analysis_maps_all_four_parts():
    analysis_output = {
        "overview": "The product has strong retention but weak acquisition.",
        "strengths": ["High week-4 retention"],
        "weaknesses": ["CAC is unmodeled"],
        "opportunities": ["Referral loop"],
        "threats": ["Paid channel saturation"],
        "key_insights": ["Retention curve flattens after week 6, not before"],
        "recommended_focus": "Model and cut CAC before scaling paid spend.",
    }

    result = FourPartContractMapper.from_analysis(analysis_output, model_used="claude-sonnet-4.5")

    assert result.core_insight == analysis_output["overview"]
    assert result.system_blueprint["opportunities"] == analysis_output["opportunities"]
    assert result.leverage_point == analysis_output["recommended_focus"]
    assert result.executable_output == analysis_output["key_insights"]
    assert result.source_engine == "analysis_engine"


def test_from_task_type_dispatches_correctly():
    plan_output = {"objective": "x", "phases": [], "milestones": [], "critical_path": [], "first_24_hours": []}
    result = FourPartContractMapper.from_task_type("plan", plan_output)
    assert result.source_engine == "plan_builder_engine"

    analysis_output = {
        "overview": "x", "strengths": [], "weaknesses": [], "opportunities": [],
        "threats": [], "key_insights": [], "recommended_focus": "y",
    }
    result = FourPartContractMapper.from_task_type("analysis", analysis_output)
    assert result.source_engine == "analysis_engine"

    strategy_output = {"summary": "x", "steps": [], "risks": [], "resources": [], "next_action": "y"}
    result = FourPartContractMapper.from_task_type("strategy", strategy_output)
    assert result.source_engine == "strategy_engine"

    # Unknown task type keys fall back to the strategy mapper rather than raising.
    result = FourPartContractMapper.from_task_type("general", strategy_output)
    assert result.source_engine == "strategy_engine"


# ---------------------------------------------------------------------------
# Fabrication guard: a parse-failure fallback must not be canonized
# ---------------------------------------------------------------------------

STRATEGY_FABRICATED = {
    "summary": "Some raw text the model returned",
    "steps": ["Review the generated content and extract actionable steps"],
    "risks": ["Response was not in expected JSON format"],
    "resources": [],
    "next_action": "Retry with a more specific goal",
}

PLAN_FABRICATED = {
    "objective": "x",
    "phases": [{"name": "Initial Phase", "duration": "TBD", "tasks": [{"task": "Review and refine plan", "steps": [], "owner": "Operator", "dependencies": []}]}],
    "milestones": ["Plan refinement complete"],
    "critical_path": ["Manual review required"],
    "first_24_hours": ["Retry with more specific goal"],
}

ANALYSIS_FABRICATED = {
    "overview": "Analysis of: x",
    "strengths": ["Unable to parse structured analysis"],
    "weaknesses": ["Response format error"],
    "opportunities": ["Retry with more specific subject"],
    "threats": ["Incomplete analysis"],
    "key_insights": ["raw text"],
    "recommended_focus": "Retry the analysis with clearer parameters",
}


@pytest.mark.parametrize(
    "mapper_name,fabricated",
    [
        ("from_strategy", STRATEGY_FABRICATED),
        ("from_plan", PLAN_FABRICATED),
        ("from_analysis", ANALYSIS_FABRICATED),
    ],
)
def test_fabricated_fallback_raises_instead_of_canonizing(mapper_name, fabricated):
    mapper = getattr(FourPartContractMapper, mapper_name)
    with pytest.raises(CanonContractError) as exc_info:
        mapper(fabricated)

    assert exc_info.value.raw == fabricated
    assert exc_info.value.source_engine
