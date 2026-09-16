"""
Canon Contract Model

The founding-seed output contract for Hybrid Intelligence Core:

    Core Insight -> System Blueprint -> Leverage Point -> Executable Output

This is additive infrastructure. It does not replace any engine's native
response shape (Strategy Engine's summary/steps/risks/resources/next_action,
Plan Builder's objective/phases/milestones, Analysis Engine's SWOT shape, etc.)
-- it maps an engine's existing output onto the four-part canon on top of it,
and always preserves the original payload under `raw` so nothing is lost.

Layering, per canon: ontology -> system -> mechanics -> outputs.
    - core_insight     answers "what is actually going on" (ontology)
    - system_blueprint answers "what minimum viable system handles it, and how
                         does it scale toward a maximum viable empire" (system)
    - leverage_point    is the single highest-ROI move -- the mechanic that
                         moves the other 80% (mechanics)
    - executable_output is the artifact the operator acts on today (outputs)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class FourPartOutput(BaseModel):
    """The founding four-part contract, mapped from any engine's raw output."""

    core_insight: str = Field(..., description="What is actually going on (ontology layer)")
    system_blueprint: Dict[str, Any] = Field(
        default_factory=dict,
        description="The minimum viable system and how it scales (system layer)",
    )
    leverage_point: str = Field(
        ..., description="The single highest-ROI move to make right now (mechanics layer)"
    )
    executable_output: Any = Field(
        ..., description="The concrete artifact/checklist the operator acts on (outputs layer)"
    )

    source_engine: str = Field(..., description="Engine that produced the mapped output")
    model_used: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    parse_warning: Optional[str] = Field(
        None, description="Set when the mapping had to compensate for a thin/partial engine response"
    )
    raw: Dict[str, Any] = Field(
        default_factory=dict, description="The untouched original engine output, preserved additively"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "core_insight": "The bottleneck isn't demand, it's onboarding drop-off.",
                "system_blueprint": {
                    "steps": ["Instrument the signup funnel", "Cut required fields from 12 to 3"],
                    "resources": ["Analytics access", "One frontend engineer-day"],
                },
                "leverage_point": "Cut signup form from 12 fields to 3.",
                "executable_output": "Ship the 3-field signup form this week.",
                "source_engine": "strategy_engine",
                "model_used": "claude-sonnet-4.5",
                "confidence": 0.8,
                "raw": {"summary": "...", "steps": ["..."]},
            }
        }


class CanonRunCreate(BaseModel):
    """Request to persist a canon run into the team's My Systems library."""

    goal: str = Field(..., min_length=1, max_length=4000)
    task_type: str
    four_part: FourPartOutput
    metadata: Dict[str, Any] = Field(default_factory=dict)
    title: Optional[str] = Field(None, max_length=200)


class CanonRunInDB(BaseModel):
    """A saved canon run as stored in the database."""

    id: str = Field(alias="_id")
    team_id: str
    created_by: str
    title: Optional[str] = None
    goal: str
    task_type: str
    four_part: FourPartOutput
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class CanonRunResponse(BaseModel):
    """A saved canon run returned to a client."""

    id: str
    team_id: str
    created_by: str
    title: Optional[str] = None
    goal: str
    task_type: str
    four_part: FourPartOutput
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class CanonRunListResponse(BaseModel):
    """A page of a team's My Systems library."""

    runs: List[CanonRunResponse]
    total: int
    limit: int
    offset: int
