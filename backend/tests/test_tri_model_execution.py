"""
Tri-model fallback/parallel execution tests.

Nothing in HIC previously retried a failed model call against a different
approved model. These tests prove `run_with_fallback` actually falls back,
never calls a model outside `services.model_policy.APPROVED_MODELS` (fails
closed the same way `test_model_policy.py` proves the policy itself fails
closed), and that `run_in_parallel` genuinely dispatches concurrently.
"""

import asyncio

import pytest

from services.model_policy import APPROVED_MODELS, ModelPolicyError
from services.tri_model_execution import (
    default_fallback_chain,
    run_in_parallel,
    run_with_fallback,
)


def test_default_fallback_chain_starts_with_preferred_and_stays_approved():
    chain = default_fallback_chain("gpt-5.2")
    assert chain[0] == "gpt-5.2"
    assert set(chain) <= APPROVED_MODELS
    assert set(chain) == APPROVED_MODELS  # every approved model is a fallback candidate


def test_default_fallback_chain_rejects_unapproved_preferred_model():
    with pytest.raises(ModelPolicyError):
        default_fallback_chain("gemini-3-flash")


def test_run_with_fallback_succeeds_on_first_model_with_no_fallback():
    calls = []

    async def engine_call(model):
        calls.append(model)
        return {"ok": True, "model": model}

    output, result = asyncio.run(run_with_fallback(engine_call, preferred_model="gpt-5.2"))

    assert output["model"] == "gpt-5.2"
    assert result.used_model == "gpt-5.2"
    assert result.fallback_used is False
    assert calls == ["gpt-5.2"]


def test_run_with_fallback_falls_back_after_first_model_fails():
    attempted = []

    async def engine_call(model):
        attempted.append(model)
        if model == "gpt-5.2":
            raise RuntimeError("simulated provider timeout")
        return {"ok": True, "model": model}

    output, result = asyncio.run(
        run_with_fallback(
            engine_call,
            preferred_model="gpt-5.2",
            chain=["gpt-5.2", "claude-sonnet-4.5"],
        )
    )

    assert attempted == ["gpt-5.2", "claude-sonnet-4.5"]
    assert output["model"] == "claude-sonnet-4.5"
    assert result.used_model == "claude-sonnet-4.5"
    assert result.fallback_used is True
    assert result.attempts[0].succeeded is False
    assert result.attempts[1].succeeded is True


def test_run_with_fallback_never_calls_a_blocked_model():
    attempted = []

    async def engine_call(model):
        attempted.append(model)
        return {"ok": True}

    with pytest.raises(RuntimeError):
        asyncio.run(
            run_with_fallback(
                engine_call,
                preferred_model="gpt-5.2",
                chain=["gemini-3-flash"],  # deliberately only an unapproved candidate
            )
        )

    # The blocked candidate must never reach the engine call.
    assert attempted == []


def test_run_with_fallback_raises_when_every_model_fails():
    async def engine_call(model):
        raise RuntimeError(f"{model} down")

    with pytest.raises(RuntimeError):
        asyncio.run(
            run_with_fallback(
                engine_call,
                preferred_model="gpt-5.2",
                chain=["gpt-5.2", "claude-sonnet-4.5"],
            )
        )


def test_run_in_parallel_dispatches_all_models_concurrently():
    async def engine_call(model):
        return {"model": model}

    results = asyncio.run(run_in_parallel(engine_call, ["gpt-5.2", "claude-sonnet-4.5"]))

    assert set(results.keys()) == {"gpt-5.2", "claude-sonnet-4.5"}
    for model, (output, error) in results.items():
        assert error is None
        assert output["model"] == model


def test_run_in_parallel_rejects_a_blocked_model_before_dispatch():
    async def engine_call(model):
        return {"model": model}

    with pytest.raises(ModelPolicyError):
        asyncio.run(run_in_parallel(engine_call, ["gpt-5.2", "gemini-3-flash"]))
