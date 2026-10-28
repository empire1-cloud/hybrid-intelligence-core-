"""Empire-1 model policy.

The HIC application is intentionally independent of Google/Gemini APIs.
All public model overrides pass through this policy before execution.
"""

from typing import Optional, Tuple


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


# Canonical provider routing for every approved logical model. Engines may
# override an entry in their own MODEL_CONFIG, but an approved model an engine
# does not list resolves here instead of being silently rerouted to the
# engine's default (which made execution receipts lie about the model used).
CANONICAL_PROVIDER_MAP = {
    "gpt-5.2": ("openai", "gpt-5.2"),
    "gpt-4o": ("openai", "gpt-4o"),
    "gpt-4o-mini": ("openai", "gpt-4o-mini"),
    "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
    "claude-3-5-sonnet": ("anthropic", "claude-3-5-sonnet-20241022"),
}


def _is_blocked(value: str) -> bool:
    lowered = (value or "").lower()
    return any(token in lowered for token in BLOCKED_MODEL_TOKENS)


def resolve_engine_model(
    model: Optional[str],
    model_config: Optional[dict] = None,
    default: str = DEFAULT_MODEL,
) -> Tuple[str, str, str]:
    """Resolve a requested model to ``(logical_model, provider, provider_model)``.

    This is the in-process execution boundary every engine calls from
    ``_create_chat``. It fails closed on Google/Gemini and unknown identifiers,
    and it re-checks the *provider pair* it is about to hand to the client, so a
    stale ``("gemini", ...)`` entry left in an engine's MODEL_CONFIG can never be
    dispatched even if a logical name were mis-mapped.
    """

    approved = enforce_approved_model(model, default)
    pair = (model_config or {}).get(approved) or CANONICAL_PROVIDER_MAP.get(approved)
    if pair is None:
        raise ModelPolicyError(f"No provider route for approved model: {approved}")

    provider, provider_model = pair
    if _is_blocked(provider) or _is_blocked(provider_model):
        raise ModelPolicyError(
            "Google/Gemini models are not permitted in the Empire-1 HIC stack."
        )
    return approved, provider, provider_model
