"""
Canon-layer task classification and engine keys.

Separate from `services/router.py::RoutingEngine` (which picks a *model*,
not an *engine*) and from `services/hybrid_core.py::TaskType` (the old
orchestrator's narrower 6-category classifier, whose own `ENGINE_MAP` was
declared and never read -- see `canon_orchestrator.py`). This module
classifies a prompt against the wider set of engines the canon layer can
actually reach. Neither `router.py` nor `hybrid_core.py` is modified here.

Pass 1 wired 2 engines (Strategy, Plan Builder) into the canon path, plus
Analysis. Pass 2 adds Opportunity Mapper, Evaluator, Pricing and Persona --
8 of the ~19 engines now genuinely reachable and dispatched by task type.
Still not wired: Blueprint, the anime/art-direction content engines, Money
Pipeline, Pipeline Composer, and the 12 Startup Copilot skills (a separate
product surface). Left for a pass 3, noted in the PR.
"""

import re
from typing import Dict, List

CANON_ENGINE_KEYS: List[str] = [
    "strategy",
    "plan",
    "analysis",
    "opportunity",
    "evaluator",
    "pricing",
    "persona",
]

DEFAULT_ENGINE_KEY = "strategy"

# Keyword/regex signals per engine. Scored, not first-match -- see
# classify_canon_task. Deliberately conservative about overlap: "evaluate"
# only lives under `evaluator` (scoring/go-no-go), not `analysis`
# (diagnostic/root-cause), so a prompt like "evaluate this idea" routes to
# the engine that actually produces a score instead of a SWOT.
_PATTERNS: Dict[str, List[str]] = {
    "plan": [
        r"\bplan\b", r"\broadmap\b", r"\btimeline\b", r"\bmilestones?\b",
        r"\bsequence\b", r"\bexecution plan\b", r"\bschedule\b", r"\bphases?\b",
    ],
    "analysis": [
        r"\banaly[sz]e\b", r"\bdiagnos", r"\baudit\b", r"\bwhy is\b",
        r"\bassess\b", r"\bcompare\b", r"\bswot\b", r"\broot cause\b",
        r"\bblind spots?\b",
    ],
    "opportunity": [
        r"\bopportunit", r"\bwhitespace\b", r"\bunmet need\b", r"\bquick wins?\b",
        r"\bmarket gap\b", r"\bwhere (can|should) (i|we)\b",
    ],
    "evaluator": [
        r"\bscore\b", r"\bevaluate\b", r"\bevaluation\b", r"\bgo.no.go\b",
        r"\bshould i\b", r"\bworth (it|doing|pursuing)\b", r"\brate\b", r"\bcritique\b",
    ],
    "pricing": [
        r"\bprice\b", r"\bpricing\b", r"\btiers?\b", r"\bcharge\b",
        r"\bmonetiz", r"\bsubscription price\b",
    ],
    "persona": [
        r"\bpersona\b", r"\bbuyer\b", r"\bicp\b", r"\btarget (audience|customer|user)\b",
        r"\bcustomer profile\b", r"\bideal customer\b",
    ],
}


def classify_canon_task(prompt: str) -> str:
    """Score a prompt against every engine's signal set; default to strategy.

    Ties and no-signal prompts both fall through to `strategy`, matching the
    original orchestrator's own default-to-strategy behavior.
    """
    text = prompt.lower()
    scores = {key: 0 for key in _PATTERNS}
    for key, patterns in _PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                scores[key] += 1

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return DEFAULT_ENGINE_KEY
    return best


def normalize_engine_key(task_type: str) -> str:
    """Map an incoming task_type string onto a canon engine key.

    Accepts every CANON_ENGINE_KEYS value as-is. Also accepts the old
    HybridIntelligenceCore TaskType values ("code", "quick", "general") for
    API backward-compatibility, folding them onto the strategy default --
    the same engine they resolved to before (HybridIntelligenceCore's own
    ENGINE_MAP pointed every one of those at strategy_engine too).
    """
    key = (task_type or "").strip().lower()
    if key in CANON_ENGINE_KEYS:
        return key
    return DEFAULT_ENGINE_KEY
