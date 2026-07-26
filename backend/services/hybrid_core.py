"""
Hybrid Intelligence Core

The master orchestrator that coordinates, executes, and maintains
the multi-model AI pipeline composed of specialized engines.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime, timezone

from services.router import RoutingEngine
from services.strategy_engine import StrategyEngine
from services.plan_builder import PlanBuilderEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage


class TaskType(Enum):
    """Task classification for routing."""
    STRATEGY = "strategy"
    PLAN = "plan"
    ANALYSIS = "analysis"
    CODE = "code"
    QUICK = "quick"
    GENERAL = "general"


class PipelineResult(BaseModel):
    """Standardized pipeline execution result."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class HybridIntelligenceCore:
    """Master orchestrator for the approved multi-model HIC pipeline."""

    ENGINE_MAP = {
        TaskType.STRATEGY: "strategy_engine",
        TaskType.PLAN: "plan_builder_engine",
        TaskType.ANALYSIS: "strategy_engine",
        TaskType.CODE: "strategy_engine",
        TaskType.QUICK: "strategy_engine",
        TaskType.GENERAL: "strategy_engine",
    }

    TASK_PATTERNS = {
        TaskType.STRATEGY: ["strategy", "plan", "business", "monetize", "grow", "scale", "launch"],
        TaskType.PLAN: ["execution", "timeline", "milestones", "phases", "schedule", "roadmap"],
        TaskType.ANALYSIS: ["analyze", "evaluate", "assess", "review", "diagnose", "investigate"],
        TaskType.CODE: ["code", "function", "debug", "api", "build", "implement", "program"],
        TaskType.QUICK: ["what is", "define", "quick", "simple", "list", "summarize"],
    }

    def __init__(self):
        self.execution_log: List[Dict] = []

    def classify_task(self, prompt: str) -> TaskType:
        """Classify task type from prompt."""
        prompt_lower = prompt.lower()

        for keyword in self.TASK_PATTERNS[TaskType.PLAN]:
            if keyword in prompt_lower:
                return TaskType.PLAN

        for task_type, keywords in self.TASK_PATTERNS.items():
            if task_type == TaskType.PLAN:
                continue
            for keyword in keywords:
                if keyword in prompt_lower:
                    return task_type

        return TaskType.GENERAL

    async def execute(
        self,
        prompt: str,
        task_type: Optional[TaskType] = None,
        context: Optional[str] = None,
        force_model: Optional[str] = None,
    ) -> PipelineResult:
        """Execute the complete routing, engine, canon, and drift pipeline."""
        start_time = datetime.now(timezone.utc)
        current_stage = PipelineStage.ROUTING

        try:
            if task_type is None:
                task_type = self.classify_task(prompt)

            routing_decision = RoutingEngine.route(prompt, force_model)
            selected_model = routing_decision.model

            current_stage = PipelineStage.STRATEGY
            if task_type == TaskType.PLAN:
                raw_output = await PlanBuilderEngine.build_plan_async(
                    goal=prompt,
                    context=context,
                    model=selected_model,
                )
            else:
                raw_output = await StrategyEngine.generate_async(
                    model=selected_model,
                    goal=prompt,
                    context=context,
                    tone="direct",
                )

            current_stage = PipelineStage.CANON
            cleaned_output = CanonEnforcer.normalize(raw_output)
            canon_validation = CanonEnforcer.validate(cleaned_output)

            current_stage = PipelineStage.DRIFT
            drift_report = DriftMonitor.check(cleaned_output, selected_model)

            end_time = datetime.now(timezone.utc)
            metadata = {
                "task_type": task_type.value,
                "model_used": selected_model,
                "routing_reason": routing_decision.reason,
                "canon_compliant": canon_validation["is_compliant"],
                "drift_status": drift_report.canon_compliance,
                "latency_ms": int((end_time - start_time).total_seconds() * 1000),
                "timestamp": end_time.isoformat(),
                "model_policy": "approved-non-google-only",
            }

            self._log_execution(prompt, task_type, metadata, success=True)

            return PipelineResult(
                success=True,
                data=cleaned_output,
                metadata=metadata,
            )

        except Exception as exc:
            error_response = ErrorHandler.handle(exc, current_stage)
            self._log_execution(prompt, task_type, {"error": str(exc)}, success=False)
            return PipelineResult(
                success=False,
                error=error_response.model_dump(),
            )

    async def execute_strategy(
        self,
        goal: str,
        context: Optional[str] = None,
        force_model: Optional[str] = None,
    ) -> PipelineResult:
        return await self.execute(
            prompt=goal,
            task_type=TaskType.STRATEGY,
            context=context,
            force_model=force_model,
        )

    async def execute_plan(
        self,
        goal: str,
        strategy: Optional[Dict] = None,
        context: Optional[str] = None,
        force_model: Optional[str] = None,
    ) -> PipelineResult:
        if strategy:
            import json
            strategy_context = f"Strategy to execute:\n{json.dumps(strategy, indent=2)}"
            context = f"{context}\n\n{strategy_context}" if context else strategy_context

        return await self.execute(
            prompt=goal,
            task_type=TaskType.PLAN,
            context=context,
            force_model=force_model,
        )

    async def execute_strategy_to_plan(
        self,
        goal: str,
        context: Optional[str] = None,
        force_model: Optional[str] = None,
    ) -> PipelineResult:
        strategy_result = await self.execute_strategy(goal, context, force_model)
        if not strategy_result.success:
            return strategy_result

        return await self.execute_plan(
            goal=strategy_result.data.get("summary", goal),
            strategy=strategy_result.data,
            force_model=force_model,
        )

    async def execute_analysis(
        self,
        subject: str,
        context: Optional[str] = None,
    ) -> PipelineResult:
        analysis_prompt = f"Analyze the following: {subject}"
        return await self.execute(
            prompt=analysis_prompt,
            task_type=TaskType.ANALYSIS,
            context=context,
            force_model="claude-sonnet-4.5",
        )

    def get_execution_log(self, limit: int = 100) -> List[Dict]:
        return self.execution_log[-limit:]

    def get_system_status(self) -> Dict:
        return {
            "status": "operational",
            "core": "hybrid_intelligence_core",
            "model_policy": "approved-non-google-only",
            "engines": {
                "routing_engine": "active",
                "strategy_engine": "active",
                "plan_builder_engine": "active",
                "canon_enforcer": "active",
                "drift_monitor": "active",
                "error_handler": "active",
            },
            "models": {
                "gpt-5.2": "available",
                "gpt-4o-mini": "available",
                "claude-sonnet-4.5": "available",
            },
            "drift_report": DriftMonitor.get_drift_report("all"),
            "executions_logged": len(self.execution_log),
        }

    def _log_execution(
        self,
        prompt: str,
        task_type: Optional[TaskType],
        metadata: Dict,
        success: bool,
    ):
        self.execution_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "task_type": task_type.value if task_type else "unknown",
            "success": success,
            "metadata": metadata,
        })

        if len(self.execution_log) > 1000:
            self.execution_log = self.execution_log[-500:]


_core_instance: Optional[HybridIntelligenceCore] = None


def get_core() -> HybridIntelligenceCore:
    global _core_instance
    if _core_instance is None:
        _core_instance = HybridIntelligenceCore()
    return _core_instance
