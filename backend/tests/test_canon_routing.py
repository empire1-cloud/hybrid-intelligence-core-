"""
Canon task classification tests -- pure logic, no LLM, no network.
"""
import pytest

from services.canon_routing import CANON_ENGINE_KEYS, classify_canon_task, normalize_engine_key


@pytest.mark.parametrize(
    "prompt,expected",
    [
        ("Build me a 6-week roadmap with milestones", "plan"),
        ("Analyze why our churn spiked last month", "analysis"),
        ("Where are the whitespace opportunities in this market?", "opportunity"),
        ("Score this idea and give me a go/no-go", "evaluator"),
        ("What should I charge for this subscription tier?", "pricing"),
        ("Build me a buyer persona for our ICP", "persona"),
        ("Help me grow this business", "strategy"),  # no strong signal -> default
    ],
)
def test_classify_canon_task_routes_to_expected_engine(prompt, expected):
    assert classify_canon_task(prompt) == expected


def test_classify_canon_task_defaults_to_strategy_on_empty_prompt():
    assert classify_canon_task("") == "strategy"


def test_normalize_engine_key_accepts_every_canon_key():
    for key in CANON_ENGINE_KEYS:
        assert normalize_engine_key(key) == key


@pytest.mark.parametrize("legacy", ["code", "quick", "general", "", None, "made_up_key"])
def test_normalize_engine_key_falls_back_to_strategy_for_unknown_or_legacy_values(legacy):
    assert normalize_engine_key(legacy) == "strategy"


def test_normalize_engine_key_is_case_insensitive():
    assert normalize_engine_key("PRICING") == "pricing"
    assert normalize_engine_key(" pricing ") == "pricing"
