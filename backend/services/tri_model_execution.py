"""
Tri-Model Execution

Founding canon calls for a hybrid tri-model stack: GPT-5.2 + Claude Sonnet 4.5
+ Gemini 3 Flash, run with parallel calls and fallbacks. The live, tested
policy in `services/model_policy.py` deliberately blocks every Google/Gemini
model at the API boundary (`test_app_contract.py::test_google_models_blocked_at_api_boundary`,
`test_model_policy.py::test_google_family_models_are_blocked`) -- that policy
is not something this pass touches or overrides.

So today, honestly: this is a dual-model (GPT-5.2 / Claude Sonnet 4.5) fallback
and parallel-race layer, not a literal tri-model one, because the third leg of
the founding canon's model list is presently forbidden by HIC's own tested
security policy. Nothing here special-cases Gemini back in. If HIC's model
policy is ever widened to approve a third provider, this module becomes
genuinely tri-model automatically -- it reads `APPROVED_MODELS` at call time
rather than hardcoding a model count.

What is real here, and did not exist anywhere in the codebase before: no
engine call in HIC previously retried against a second model on failure, and
no engine call ran two models concurrently. `RoutingEngine.route()` always
picked exactly one model with no fallback path.
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional

from pydantic import BaseModel

from services.model_policy import APPROVED_MODELS, ModelPolicyError, enforce_approved_model

EngineCall = Callable[[str], Awaitable[Dict[str, Any]]]


class ModelAttempt(BaseModel):
    model: str
    succeeded: bool
    error: Optional[str] = None


class TriModelResult(BaseModel):
    """Metadata describing how a call was actually executed."""

    requested_model: str
    used_model: str
    fallback_used: bool
    attempts: List[ModelAttempt]


def default_fallback_chain(preferred_model: str) -> List[str]:
    """Build a fallback chain starting at the preferred approved model.

    Every other currently-approved model becomes a fallback, in a stable
    order, so a policy change to APPROVED_MODELS is picked up automatically
    without editing this function.
    """
    preferred = enforce_approved_model(preferred_model)
    rest = sorted(model for model in APPROVED_MODELS if model != preferred)
    return [preferred, *rest]


async def run_with_fallback(
    engine_call: EngineCall,
    preferred_model: str,
    chain: Optional[List[str]] = None,
) -> "tuple[Dict[str, Any], TriModelResult]":
    """Call `engine_call(model)` against each approved model in `chain` until one succeeds.

    `engine_call` is any coroutine function taking an approved model name and
    returning the engine's raw output dict (e.g. `StrategyEngine.generate_async`
    partially applied over everything except `model`). Every model in the
    chain is validated through `enforce_approved_model` before use -- a caller
    cannot smuggle a blocked model in via a custom chain.
    """
    resolved_chain = chain or default_fallback_chain(preferred_model)
    attempts: List[ModelAttempt] = []
    last_error: Optional[Exception] = None

    for candidate in resolved_chain:
        try:
            approved = enforce_approved_model(candidate)
        except ModelPolicyError as exc:
            attempts.append(ModelAttempt(model=candidate, succeeded=False, error=str(exc)))
            last_error = exc
            continue

        try:
            output = await engine_call(approved)
            attempts.append(ModelAttempt(model=approved, succeeded=True))
            result = TriModelResult(
                requested_model=enforce_approved_model(preferred_model),
                used_model=approved,
                fallback_used=approved != enforce_approved_model(preferred_model),
                attempts=attempts,
            )
            return output, result
        except Exception as exc:  # noqa: BLE001 - any provider/transport failure triggers fallback
            attempts.append(ModelAttempt(model=approved, succeeded=False, error=str(exc)))
            last_error = exc
            continue

    raise RuntimeError(
        f"All models in the fallback chain failed: {[a.model for a in attempts]}"
    ) from last_error


async def run_in_parallel(
    engine_call: EngineCall,
    models: List[str],
) -> Dict[str, "tuple[Optional[Dict[str, Any]], Optional[str]]"]:
    """Race the same engine call concurrently across several approved models.

    Returns a dict keyed by model name to (output, error) -- output is None if
    that model's call failed. Every model is policy-checked before dispatch.
    Useful for a consensus/compare view rather than a single best-effort answer.
    """
    approved_models = [enforce_approved_model(model) for model in models]

    async def _call(model: str):
        try:
            return model, await engine_call(model), None
        except Exception as exc:  # noqa: BLE001
            return model, None, str(exc)

    results = await asyncio.gather(*(_call(model) for model in approved_models))
    return {model: (output, error) for model, output, error in results}
