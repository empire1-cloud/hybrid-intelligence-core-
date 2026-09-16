"""
Canon Contract Mapper

Maps an existing engine's native output onto the founding four-part contract
(Core Insight -> System Blueprint -> Leverage Point -> Executable Output)
without changing the engine itself.

This module also closes a known gap the same way `startup_copilot_engines.py`
already closed it for the 12 founder skills (see `SkillOutputError` there):
`strategy_engine.py`, `plan_builder.py` and `analysis_engine.py` each still
fall back to hardcoded placeholder text ("Retry with a more specific goal",
"Unable to parse structured analysis", etc.) when the model's response does
not parse as JSON. Mapping that placeholder text into a canon output would
present a fabricated system as insight. `CanonContractError` is raised
instead -- callers get an honest failure, matching the pattern already proven
in `startup_copilot_engines.py::SkillOutputError`. The underlying engines are
untouched; this module only refuses to *trust* their fallback shape.
"""

from typing import Any, Dict


class CanonContractError(RuntimeError):
    """Raised when an engine's response cannot be trusted enough to canonize."""

    def __init__(self, message: str, source_engine: str, raw: Dict[str, Any]):
        self.source_engine = source_engine
        self.raw = raw
        super().__init__(message)


# Literal strings each engine's own JSONDecodeError fallback is known to emit.
# These are the "fabrication signatures" -- if any is present, the underlying
# engine did not get a parseable response and manufactured placeholder text.
_STRATEGY_FABRICATION_MARKERS = (
    "Retry with a more specific goal",
    "Response was not in expected JSON format",
)
_PLAN_FABRICATION_MARKERS = (
    "Manual review required",
    "Retry with more specific goal",
)
_ANALYSIS_FABRICATION_MARKERS = (
    "Unable to parse structured analysis",
    "Retry the analysis with clearer parameters",
)


def _contains_any(haystack: Any, markers: tuple) -> bool:
    """True if any marker string appears anywhere in a (possibly nested) value."""
    if isinstance(haystack, str):
        return any(marker in haystack for marker in markers)
    if isinstance(haystack, list):
        return any(_contains_any(item, markers) for item in haystack)
    if isinstance(haystack, dict):
        return any(_contains_any(value, markers) for value in haystack.values())
    return False


class FourPartContractMapper:
    """Maps native engine output dicts onto `FourPartOutput`."""

    @staticmethod
    def from_strategy(output: Dict[str, Any], model_used: str = None) -> "FourPartOutput":
        from models.canon_contract import FourPartOutput

        if _contains_any(output, _STRATEGY_FABRICATION_MARKERS):
            raise CanonContractError(
                "Strategy Engine response did not parse; refusing to canonize a fabricated fallback.",
                source_engine="strategy_engine",
                raw=output,
            )

        steps = output.get("steps") or []
        resources = output.get("resources") or []
        risks = output.get("risks") or []
        next_action = output.get("next_action") or ""

        return FourPartOutput(
            core_insight=output.get("summary", ""),
            system_blueprint={"steps": steps, "resources": resources, "risks": risks},
            leverage_point=next_action or (steps[0] if steps else ""),
            executable_output=steps or next_action,
            source_engine="strategy_engine",
            model_used=model_used,
            raw=output,
        )

    @staticmethod
    def from_plan(output: Dict[str, Any], model_used: str = None) -> "FourPartOutput":
        from models.canon_contract import FourPartOutput

        if _contains_any(output, _PLAN_FABRICATION_MARKERS):
            raise CanonContractError(
                "Plan Builder response did not parse; refusing to canonize a fabricated fallback.",
                source_engine="plan_builder_engine",
                raw=output,
            )

        phases = output.get("phases") or []
        milestones = output.get("milestones") or []
        critical_path = output.get("critical_path") or []
        first_24_hours = output.get("first_24_hours") or []

        return FourPartOutput(
            core_insight=output.get("objective", ""),
            system_blueprint={"phases": phases, "milestones": milestones},
            leverage_point=(critical_path[0] if critical_path else (milestones[0] if milestones else "")),
            executable_output=first_24_hours or phases,
            source_engine="plan_builder_engine",
            model_used=model_used,
            raw=output,
        )

    @staticmethod
    def from_analysis(output: Dict[str, Any], model_used: str = None) -> "FourPartOutput":
        from models.canon_contract import FourPartOutput

        if _contains_any(output, _ANALYSIS_FABRICATION_MARKERS):
            raise CanonContractError(
                "Analysis Engine response did not parse; refusing to canonize a fabricated fallback.",
                source_engine="analysis_engine",
                raw=output,
            )

        key_insights = output.get("key_insights") or []

        return FourPartOutput(
            core_insight=output.get("overview", ""),
            system_blueprint={
                "strengths": output.get("strengths") or [],
                "weaknesses": output.get("weaknesses") or [],
                "opportunities": output.get("opportunities") or [],
                "threats": output.get("threats") or [],
            },
            leverage_point=output.get("recommended_focus", ""),
            executable_output=key_insights,
            source_engine="analysis_engine",
            model_used=model_used,
            raw=output,
        )

    @classmethod
    def from_task_type(cls, task_type: str, output: Dict[str, Any], model_used: str = None) -> "FourPartOutput":
        """Dispatch to the mapper for a given orchestrator task type."""
        mappers = {
            "plan": cls.from_plan,
            "analysis": cls.from_analysis,
        }
        mapper = mappers.get(task_type, cls.from_strategy)
        return mapper(output, model_used=model_used)
