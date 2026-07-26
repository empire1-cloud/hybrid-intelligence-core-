"""Empire-1 model policy.

The HIC application is intentionally independent of Google/Gemini APIs.
All public model overrides pass through this policy before execution.
"""

from typing import Optional


class ModelPolicyError(ValueError):
    """Raised when a requested model is outside the approved HIC stack."""


APPROVED_MODELS = {
    "gpt-5.2",
    "gpt-4o",
    "gpt-4o-mini",
    "claude-sonnet-4.5",
    "claude-3-5-sonnet",
}

BLOCKED_MODEL_TOKENS = ("gemini", "google", "vertex")
DEFAULT_MODEL = "gpt-5.2"
QUICK_MODEL = "gpt-4o-mini"


def enforce_approved_model(model: Optional[str], default: str = DEFAULT_MODEL) -> str:
    """Return an approved model name or fail closed.

    Unknown and Google-family model names are rejected rather than silently
    rerouted so execution receipts remain truthful about the requested model.
    """

    candidate = (model or default).strip().lower()

    if any(token in candidate for token in BLOCKED_MODEL_TOKENS):
        raise ModelPolicyError(
            "Google/Gemini models are not permitted in the Empire-1 HIC stack."
        )

    if candidate not in APPROVED_MODELS:
        raise ModelPolicyError(f"Model is not approved for HIC execution: {candidate}")

    return candidate
