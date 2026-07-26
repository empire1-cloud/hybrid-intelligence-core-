import pytest

from services.model_policy import (
    DEFAULT_MODEL,
    QUICK_MODEL,
    ModelPolicyError,
    enforce_approved_model,
)


def test_default_model_is_approved():
    assert enforce_approved_model(None) == DEFAULT_MODEL


def test_quick_model_is_approved():
    assert enforce_approved_model(QUICK_MODEL) == "gpt-4o-mini"


@pytest.mark.parametrize(
    "blocked_model",
    [
        "gemini-3-flash",
        "google/gemini-2.5-pro",
        "vertex-ai-gemini",
    ],
)
def test_google_family_models_are_blocked(blocked_model):
    with pytest.raises(ModelPolicyError, match="not permitted"):
        enforce_approved_model(blocked_model)


def test_unknown_model_fails_closed():
    with pytest.raises(ModelPolicyError, match="not approved"):
        enforce_approved_model("mystery-model")
