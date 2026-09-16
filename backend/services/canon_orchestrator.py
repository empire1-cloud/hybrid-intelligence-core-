"""
Canon Orchestrator

An additive execution path alongside `services/hybrid_core.py::HybridIntelligenceCore`.
It does not replace, import-shadow, or modify that class -- `/api/core/execute`
keeps behaving exactly as it does today. This is a second, opt-in path
(`/api/canon/execute`) that closes three verified gaps in the existing
orchestrator without touching it:

1. `HybridIntelligenceCore.execute()` only ever calls `StrategyEngine` or
   `PlanBuilderEngine`, regardless of task type -- its own `ENGINE_MAP` dict is
   declared and never read anywhere else in that file. `CanonicalOrchestrator`
   actually dispatches Analysis-classified prompts to `AnalysisEngine`.
2. Nothing in HIC retries a failed model call against a different approved
   model, and nothing runs two approved models concurrently. This orchestrator
   runs every engine call through `services/tri_model_execution.run_with_fallback`.
3. No engine emits the founding four-part contract (Core Insight -> System
   Blueprint -> Leverage Point -> Executable Output). This orchestrator maps
   every engine's native output onto that contract via
   `services/canon_contract.FourPartContractMapper`, and refuses to canonize a
   response it detects as a fabricated parse-failure fallback.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel

from services.analysis_engine import AnalysisEngine
from services.canon_contract import CanonContractError, FourPartContractMapper
from services.error_handler import ErrorHandler, PipelineStage
from services.hybrid_core import TaskType, get_core
from services.plan_builder import PlanBuilderEngine
from services.router import RoutingEngine
from services.strategy_engine import StrategyEngine
from services.tri_model_execution import default_fallback_chain, run_with_fallback


class CanonPipelineResult(BaseModel):
    """Result of a canon-contract execution."""

    success: bool
    four_part: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


_ENGINE_CALLERS = {
    TaskType.ANALYSIS: lambda prompt, context: (
        lambda model: AnalysisEngine.analyze_async(subject=prompt, context=context, model=model)
    ),
    TaskType.PLAN: lambda prompt, context: (
        lambda model: PlanBuilderEngine.build_plan_async(goal=prompt, context=context, model=model)
    ),
}


def _default_caller(prompt: str, context: Optional[str]):
    return lambda model: StrategyEngine.generate_async(model=model, goal=prompt, context=context, tone="direct")


def _task_type_key(task_type: TaskType) -> str:
    """Map a TaskType onto the mapper keys the contract layer understands."""
    if task_type == TaskType.PLAN:
        return "plan"
    if task_type == TaskType.ANALYSIS:
        return "analysis"
    return "strategy"


class CanonicalOrchestrator:
    """Runs the routing -> engine -> fallback -> four-part-contract pipeline."""

    async def execute(
        self,
        prompt: str,
        task_type: Optional[TaskType] = None,
        context: Optional[str] = None,
        force_model: Optional[str] = None,
    ) -> CanonPipelineResult:
        start_time = datetime.now(timezone.utc)

        try:
            core = get_core()
            if task_type is None:
                task_type = core.classify_task(prompt)

            routing_decision = RoutingEngine.route(prompt, force_model)

            caller_factory = _ENGINE_CALLERS.get(task_type, _default_caller)
            engine_call = caller_factory(prompt, context)

            chain = default_fallback_chain(routing_decision.model)
            raw_output, tri_model_result = await run_with_fallback(
                engine_call=engine_call,
                preferred_model=routing_decision.model,
                chain=chain,
            )

            task_key = _task_type_key(task_type)
            four_part = FourPartContractMapper.from_task_type(
                task_key, raw_output, model_used=tri_model_result.used_model
            )

            end_time = datetime.now(timezone.utc)
            metadata = {
                "task_type": task_type.value,
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
