"""
Canon Orchestrator

An additive execution path alongside `services/hybrid_core.py::HybridIntelligenceCore`.
It does not replace, import-shadow, or modify that class -- `/api/core/execute`
keeps behaving exactly as it does today. This is a second, opt-in path
(`/api/canon/execute`) that closes verified gaps in the existing orchestrator
without touching it:

1. `HybridIntelligenceCore.execute()` only ever calls `StrategyEngine` or
   `PlanBuilderEngine`, regardless of task type -- its own `ENGINE_MAP` dict is
   declared and never read anywhere else in that file. Pass 1 wired Analysis
   in; pass 2 wires in Opportunity Mapper, Evaluator, Pricing and Persona too
   (see `services/canon_routing.py` for the classifier and the full list of
   what's still not reachable). 8 of ~19 engines are now genuinely dispatched
   by task type through this path.
2. Nothing in HIC retries a failed model call against a different approved
   model, and nothing runs two approved models concurrently. This orchestrator
   runs every engine call through `services/tri_model_execution.run_with_fallback`.
3. No engine emits the founding four-part contract (Core Insight -> System
   Blueprint -> Leverage Point -> Executable Output). This orchestrator maps
   every engine's native output onto that contract via
   `services/canon_contract.FourPartContractMapper`, and refuses to canonize a
   response it detects as a fabricated parse-failure fallback. As of pass 2,
   Strategy/Plan/Analysis no longer produce that fallback at all -- they raise
   `EngineOutputError` at the source (see `services/engine_errors.py`); the
   mapper's detection for those three is now defense-in-depth, not load-bearing.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel

from services.analysis_engine import AnalysisEngine
from services.canon_contract import CanonContractError, FourPartContractMapper
from services.canon_routing import classify_canon_task, normalize_engine_key
from services.error_handler import ErrorHandler, PipelineStage
from services.evaluator_engine import EvaluatorEngine
from services.opportunity_mapper import OpportunityMapperEngine
from services.persona_engine import PersonaEngine
from services.plan_builder import PlanBuilderEngine
from services.pricing_engine import PricingEngine
from services.router import RoutingEngine
from services.strategy_engine import StrategyEngine
from services.tri_model_execution import default_fallback_chain, run_with_fallback


class CanonPipelineResult(BaseModel):
    """Result of a canon-contract execution."""

    success: bool
    four_part: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


# Each factory takes (prompt, context) and returns a callable of (model) ->
# awaitable engine output dict, so tri_model_execution.run_with_fallback can
# retry the same call against a different approved model.
_ENGINE_CALLERS = {
    "analysis": lambda prompt, context: (
        lambda model: AnalysisEngine.analyze_async(subject=prompt, context=context, model=model)
    ),
    "plan": lambda prompt, context: (
        lambda model: PlanBuilderEngine.build_plan_async(goal=prompt, context=context, model=model)
    ),
    "opportunity": lambda prompt, context: (
        lambda model: OpportunityMapperEngine.map_opportunities_async(
            situation=prompt, context=context, model=model
        )
    ),
    "evaluator": lambda prompt, context: (
        lambda model: EvaluatorEngine.evaluate_async(
            subject=prompt, content=(context or prompt), model=model
        )
    ),
    "pricing": lambda prompt, context: (
        lambda model: PricingEngine.generate_pricing_async(product=prompt, description=context, model=model)
    ),
    "persona": lambda prompt, context: (
        lambda model: PersonaEngine.generate_persona_async(audience=prompt, context=context, model=model)
    ),
}


def _default_caller(prompt: str, context: Optional[str]):
    return lambda model: StrategyEngine.generate_async(model=model, goal=prompt, context=context, tone="direct")


class CanonicalOrchestrator:
    """Runs the routing -> engine -> fallback -> four-part-contract pipeline."""

    async def execute(
        self,
        prompt: str,
        task_type: Optional[str] = None,
        context: Optional[str] = None,
        force_model: Optional[str] = None,
    ) -> CanonPipelineResult:
        start_time = datetime.now(timezone.utc)

        try:
            engine_key = normalize_engine_key(task_type) if task_type else classify_canon_task(prompt)

            routing_decision = RoutingEngine.route(prompt, force_model)

            caller_factory = _ENGINE_CALLERS.get(engine_key, _default_caller)
            engine_call = caller_factory(prompt, context)

            chain = default_fallback_chain(routing_decision.model)
            raw_output, tri_model_result = await run_with_fallback(
                engine_call=engine_call,
                preferred_model=routing_decision.model,
                chain=chain,
            )

            four_part = FourPartContractMapper.from_task_type(
                engine_key, raw_output, model_used=tri_model_result.used_model
            )

            end_time = datetime.now(timezone.utc)
            metadata = {
                "task_type": engine_key,
                "canon_layer": "ontology-system-mechanics-outputs",
                "routing_reason": routing_decision.reason,
                "requested_model": tri_model_result.requested_model,
                "model_used": tri_model_result.used_model,
                "fallback_used": tri_model_result.fallback_used,
                "attempts": [a.model_dump() for a in tri_model_result.attempts],
                "latency_ms": int((end_time - start_time).total_seconds() * 1000),
                "timestamp": end_time.isoformat(),
                "model_policy": "approved-non-google-only",
            }

            return CanonPipelineResult(
                success=True,
                four_part=four_part.model_dump(),
                metadata=metadata,
            )

        except CanonContractError as exc:
            error_response = ErrorHandler.create_error(
                error_type=ErrorHandler.classify_error(exc, PipelineStage.CANON),
                stage=PipelineStage.CANON,
                message=str(exc),
            )
            return CanonPipelineResult(success=False, error=error_response.model_dump())

        except Exception as exc:  # noqa: BLE001 - surfaced as a structured pipeline error
            error_response = ErrorHandler.handle(exc, PipelineStage.ORCHESTRATOR)
            return CanonPipelineResult(success=False, error=error_response.model_dump())


_orchestrator_instance: Optional[CanonicalOrchestrator] = None


def get_canonical_orchestrator() -> CanonicalOrchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = CanonicalOrchestrator()
    return _orchestrator_instance
