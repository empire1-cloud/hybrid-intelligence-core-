"""
Shared error type for engines that refuse to fabricate output on a parse
failure, instead of silently returning hardcoded placeholder text disguised
as a real result.

Mirrors `services/startup_copilot_engines.py::SkillOutputError`, which
already proved this exact fix for the 12 founder skills (see
`test_startup_copilot_contract.py::test_unparseable_response_raises_instead_of_fabricating`).
This is the same fix applied to `strategy_engine.py`, `plan_builder.py` and
`analysis_engine.py`.

Every existing caller of these three engines already wraps the call in
`try/except Exception -> a structured error response`:
`routers/engines/strategy.py`, `routers/engines/plan.py`,
`routers/engines/analysis.py`, and `services/hybrid_core.py::execute()`.
Raising here does not introduce an unhandled failure anywhere it is called
from today -- it replaces a silent fabricated 200 with an honest
500 / structured `PipelineResult(success=False, ...)`.
"""


class EngineOutputError(RuntimeError):
    """Raised when an engine's LLM response cannot be parsed into its schema."""

    def __init__(self, message: str, response_text: str = ""):
        self.response_text = response_text
        super().__init__(message)
