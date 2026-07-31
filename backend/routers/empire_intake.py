"""Map outside signals into existing Empire-1 product lanes."""
from __future__ import annotations

import hashlib
import re
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/empire1/intake", tags=["Empire-1 Intake"])


class EmpireSignalRequest(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    summary: str = Field(min_length=2, max_length=5000)
    source_type: Literal[
        "article", "repository", "product", "feature", "customer_request", "research", "other"
    ] = "other"
    source_url: str | None = Field(default=None, max_length=2000)
    stated_goal: str | None = Field(default=None, max_length=1000)


class EmpireSignalResponse(BaseModel):
    intake_id: str
    status: Literal["READY_FOR_EXECUTION", "NEEDS_FOUNDER_PLACEMENT"]
    empire_parent: str
    primary_lane: str
    supporting_lanes: list[str]
    decision: Literal["EVOLVE_EXISTING"]
    new_universe_allowed: bool
    new_repository_allowed: bool
    empire_version: str
    reuse: list[str]
    revenue_path: str
    complete_loop: list[str]
    evidence_required: list[str]
    completion_gate: str


LANES = (
    {
        "name": "Archisynapse — Empire-1 Financial Infrastructure",
        "keywords": {"payment", "payments", "ledger", "fraud", "billing", "spend", "refund", "reconciliation", "financial", "fintech", "invoice"},
        "support": ["Empire-1 HIC", "FABLE-5"],
        "reuse": ["signed receipts", "double-entry ledger", "idempotency and governed spend controls"],
        "revenue": "technical evaluation, paid pilot, then recurring infrastructure contract",
    },
    {
        "name": "Lyrica 3 — Empire-1 Creator-Owned Music Platform",
        "keywords": {"music", "song", "singing", "singer", "vocal", "vocals", "voice", "artist", "remix", "royalty", "audio", "daw", "producer"},
        "support": ["Soulfire", "Cultura", "Archisynapse", "Empire-1 HIC"],
        "reuse": ["Sonance Pro and SL Universal", "Soulfire emotional controls", "DNA, Soulprint, VICS, provenance, and royalty receipts"],
        "revenue": "creator subscription, professional tools, licensing, and governed remix revenue",
    },
    {
        "name": "Southern Lifestyle Universal Game OS — Empire-1",
        "keywords": {"game", "games", "gaming", "arcade", "mechanic", "mechanics", "tournament"},
        "support": ["SLA113", "Cultura", "Empire-1 HIC", "Archisynapse"],
        "reuse": ["SLA113 tenant controls", "Southern game runtime", "Cultura theme and authenticity logic"],
        "revenue": "setup fee plus recurring operator and license revenue",
    },
    {
        "name": "Cultura — Empire-1 Cultural Intelligence",
        "keywords": {"culture", "cultural", "dialect", "heritage", "authenticity", "community", "regional", "localization", "tradition"},
        "support": ["Empire-1 HIC", "Lyrica 3", "Southern Lifestyle Universal Game OS"],
        "reuse": ["Cultura respect protocols", "Taller and Vibe Forge", "HIC evaluation and drift controls"],
        "revenue": "licensed cultural-intelligence capability and embedded expansion",
    },
    {
        "name": "SLA113 — Empire-1 Control Plane and Product Factory",
        "keywords": {"tenant", "multitenant", "policy", "governance", "operator", "factory", "deployment"},
        "support": ["Empire-1 HIC", "FABLE-5"],
        "reuse": ["tenant registry", "policy and identity boundaries", "deployment and evidence controls"],
        "revenue": "enterprise implementation plus recurring control-plane license",
    },
    {
        "name": "Empire-1 HIC — Intelligence and Execution Core",
        "keywords": {"ai", "agent", "agents", "model", "models", "workflow", "automation", "pipeline", "orchestration", "analytics", "engine", "routing", "evaluation", "dashboard", "api"},
        "support": ["SLA113", "FABLE-5"],
        "reuse": ["19-engine registry", "Pipeline Composer and execution history", "workspaces, API keys, usage, and billing"],
        "revenue": "paid HIC workspace, enterprise subscription, or scoped implementation",
    },
)


def _tokens(value: str) -> set[str]:
    return {part for part in re.sub(r"[^a-z0-9]+", " ", value.lower()).split() if part}


def classify_empire_signal(request: EmpireSignalRequest) -> EmpireSignalResponse:
    text = " ".join(filter(None, [request.title, request.summary, request.stated_goal or ""]))
    tokens = _tokens(text)
    ranked = sorted(
        ((len(tokens & lane["keywords"]), index, lane) for index, lane in enumerate(LANES)),
        key=lambda item: (-item[0], item[1]),
    )
    score, _, lane = ranked[0]
    if score == 0:
        lane = LANES[-1]
    seed = f"{request.source_type}|{request.title}|{request.source_url or ''}|{request.summary}"
    intake_id = f"empint_{hashlib.sha256(seed.encode()).hexdigest()[:16]}"
    return EmpireSignalResponse(
        intake_id=intake_id,
        status="READY_FOR_EXECUTION" if score else "NEEDS_FOUNDER_PLACEMENT",
        empire_parent="Empire-1",
        primary_lane=lane["name"],
        supporting_lanes=lane["support"],
        decision="EVOLVE_EXISTING",
        new_universe_allowed=False,
        new_repository_allowed=False,
        empire_version=(
            f"Build the Empire-1 version of '{request.title}' inside {lane['name']}; "
            "reuse proven architecture, replace outside identity and assumptions, and connect revenue and evidence."
        ),
        reuse=lane["reuse"],
        revenue_path=lane["revenue"],
        complete_loop=[
            "inspect the canonical repository and current implementation",
            "reuse existing components and reject duplicate architecture",
            "implement one complete customer-operational loop",
            "add authentication, persistence, failure handling, recovery, evidence, and money controls where applicable",
            "test, merge, deploy or prove a reproducible runtime, and issue an exact receipt",
        ],
        evidence_required=[
            "canonical repository and exact commit",
            "success, denial, failure, and recovery tests",
            "deployment or runnable-environment proof",
            "honest claim boundaries",
            "revenue path and customer acceptance criteria",
        ],
        completion_gate=(
            "Never mark finished until the founder-approved loop is merged, operational, secured, "
            "recovery-tested, documented, monetized where applicable, and evidenced."
        ),
    )


@router.post("/map", response_model=EmpireSignalResponse)
async def map_empire_signal(request: EmpireSignalRequest) -> EmpireSignalResponse:
    return classify_empire_signal(request)
