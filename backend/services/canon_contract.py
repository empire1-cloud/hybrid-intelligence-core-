"""
Canon Contract Mapper

Maps an existing engine's native output onto the founding four-part contract
(Core Insight -> System Blueprint -> Leverage Point -> Executable Output)
without changing the engine's prompt, schema, or model selection.

Pass 1 found that `strategy_engine.py`, `plan_builder.py` and
`analysis_engine.py` each fell back to hardcoded placeholder text ("Retry
with a more specific goal", "Unable to parse structured analysis", etc.) on
a JSON parse failure, and this module detected that shape and raised
`CanonContractError` instead of canonizing it -- an honest failure at the
mapping layer, matching the pattern already proven in
`startup_copilot_engines.py::SkillOutputError`.

Pass 2 fixed the three engines themselves (see `services/engine_errors.py`
and the `except json.JSONDecodeError` blocks in each of those three files):
they now raise `EngineOutputError` at the source instead of returning
fabricated placeholder JSON, so `from_strategy`/`from_plan`/`from_analysis`
will in practice never see that shape anymore. The marker checks below are
kept as defense-in-depth (belt-and-suspenders, not load-bearing) rather than
removed -- WE EVOLVE, NEVER DELETE.

Opportunity Mapper, Evaluator, Pricing and Persona are newly wired into the
canon layer in pass 2 (see `canon_orchestrator.py` /
`canon_routing.py`). Those four engines were *not* fixed at the source in
this pass -- they still fabricate a placeholder on parse failure -- so their
mappers below still do the load-bearing detection work pass 1 established.
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
_OPPORTUNITY_FABRICATION_MARKERS = (
    "Response parsing failed - retry with clearer situation description",
    "Provide a more specific situation description",
)
_EVALUATOR_FABRICATION_MARKERS = (
    "Unable to parse evaluation",
    "Retry with clearer content",
)
_PRICING_FABRICATION_MARKERS = (
    "Pricing not generated - retry required",
)
_PERSONA_FABRICATION_MARKERS = (
    "Persona generation failed - retry required",
    "Unnamed Persona",
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

    @staticmethod
    def from_opportunity(output: Dict[str, Any], model_used: str = None) -> "FourPartOutput":
        from models.canon_contract import FourPartOutput

        if _contains_any(output, _OPPORTUNITY_FABRICATION_MARKERS):
            raise CanonContractError(
                "Opportunity Mapper response did not parse; refusing to canonize a fabricated fallback.",
                source_engine="opportunity_mapper_engine",
                raw=output,
            )

        opportunities = output.get("opportunities") or []
        top_3 = output.get("top_3_opportunities") or []

        return FourPartOutput(
            core_insight=output.get("context_summary", ""),
            system_blueprint={"opportunities": opportunities},
            leverage_point=output.get("recommended_next_move", ""),
            executable_output=top_3 or opportunities,
            source_engine="opportunity_mapper_engine",
            model_used=model_used,
            raw=output,
        )

    @staticmethod
    def from_evaluator(output: Dict[str, Any], model_used: str = None) -> "FourPartOutput":
        from models.canon_contract import FourPartOutput

        if _contains_any(output, _EVALUATOR_FABRICATION_MARKERS):
            raise CanonContractError(
                "Evaluator Engine response did not parse; refusing to canonize a fabricated fallback.",
                source_engine="evaluator_engine",
                raw=output,
            )

        subject = output.get("subject", "")
        weighted_score = output.get("weighted_score", 0)
        go_no_go = output.get("go_no_go", "")
        improvements = output.get("improvement_suggestions") or []
        strengths = output.get("strengths") or []

        return FourPartOutput(
            core_insight=f"{subject} scored {weighted_score}/10 -- {go_no_go}".strip(),
            system_blueprint={
                "criteria": output.get("criteria") or [],
                "weighted_score": weighted_score,
            },
            leverage_point=(improvements[0] if improvements else (strengths[0] if strengths else "")),
            executable_output=improvements,
            source_engine="evaluator_engine",
            model_used=model_used,
            raw=output,
        )

    @staticmethod
    def from_pricing(output: Dict[str, Any], model_used: str = None) -> "FourPartOutput":
        from models.canon_contract import FourPartOutput

        if _contains_any(output, _PRICING_FABRICATION_MARKERS):
            raise CanonContractError(
                "Pricing Engine response did not parse; refusing to canonize a fabricated fallback.",
                source_engine="pricing_engine",
                raw=output,
            )

        tiers = output.get("tiers") or []
        entry_tier = output.get("recommended_entry_tier", "")

        return FourPartOutput(
            core_insight=output.get("offer_summary", ""),
            system_blueprint={
                "tiers": tiers,
                "pricing_model": output.get("pricing_model", ""),
                "target_segments": output.get("target_segments") or [],
            },
            leverage_point=(f"Lead with the {entry_tier} tier." if entry_tier else ""),
            executable_output=tiers,
            source_engine="pricing_engine",
            model_used=model_used,
            raw=output,
        )

    @staticmethod
    def from_persona(output: Dict[str, Any], model_used: str = None) -> "FourPartOutput":
        from models.canon_contract import FourPartOutput

        if _contains_any(output, _PERSONA_FABRICATION_MARKERS):
            raise CanonContractError(
                "Persona Engine response did not parse; refusing to canonize a fabricated fallback.",
                source_engine="persona_engine",
                raw=output,
            )

        triggers = output.get("triggers") or []
        buying_criteria = output.get("buying_criteria") or []
        messaging = output.get("preferred_messaging") or []

        return FourPartOutput(
            core_insight=output.get("background", ""),
            system_blueprint={
                "goals": output.get("goals") or [],
                "pains": output.get("pains") or [],
                "buying_criteria": buying_criteria,
            },
            leverage_point=(triggers[0] if triggers else (buying_criteria[0] if buying_criteria else "")),
            executable_output=messaging,
            source_engine="persona_engine",
            model_used=model_used,
            raw=output,
        )

    @classmethod
    def from_task_type(cls, task_type: str, output: Dict[str, Any], model_used: str = None) -> "FourPartOutput":
        """Dispatch to the mapper for a given canon engine key (see canon_routing.CANON_ENGINE_KEYS)."""
        mappers = {
            "plan": cls.from_plan,
            "analysis": cls.from_analysis,
            "opportunity": cls.from_opportunity,
            "evaluator": cls.from_evaluator,
            "pricing": cls.from_pricing,
            "persona": cls.from_persona,
        }
        mapper = mappers.get(task_type, cls.from_strategy)
        return mapper(output, model_used=model_used)
