"""
Canon Contract endpoints.

Additive alongside `/core/*` (services/hybrid_core.py). `/canon/execute` runs
the founding four-part contract pipeline (services/canon_orchestrator.py) and
`/canon/runs*` is the team's "My Systems" library of saved outputs
(services/canon_run_service.py). Nothing here modifies `/core/*` or any
existing engine.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.engine_context import EngineContext, EngineExecutor, get_engine_context
from services.canon_orchestrator import get_canonical_orchestrator
from services.canon_run_service import (
    CanonRunError,
    delete_canon_run,
    get_canon_run_by_id,
    get_team_canon_runs,
    save_canon_run,
)
from services.canon_routing import CANON_ENGINE_KEYS
from services.model_policy import APPROVED_MODELS
from services.tri_model_execution import default_fallback_chain

router = APIRouter(prefix="/canon", tags=["canon"])


class CanonExecuteRequest(BaseModel):
    """Request for the four-part canon contract pipeline."""

    prompt: str
    task_type: Optional[str] = None
    context: Optional[str] = None
    force_model: Optional[str] = None
    save: bool = False
    title: Optional[str] = None


class CanonExecuteResponse(BaseModel):
    success: bool
    four_part: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    saved_run_id: Optional[str] = None


@router.post("/execute", response_model=CanonExecuteResponse)
async def canon_execute(
    payload: CanonExecuteRequest,
    ctx: EngineContext = Depends(get_engine_context),
):
    """Execute a prompt through the founding four-part canon contract pipeline."""
    ctx.require_write()
    orchestrator = get_canonical_orchestrator()

    async with EngineExecutor(ctx, engine="canon_orchestrator", input_data=payload.model_dump()) as ex:
        result = await orchestrator.execute(
            prompt=payload.prompt,
            task_type=payload.task_type,
            context=payload.context,
            force_model=payload.force_model,
        )
        ex.set_output(result.model_dump())

    if not result.success:
        return JSONResponse(status_code=422, content=result.error)

    saved_run_id = None
    if payload.save:
        from models.canon_contract import FourPartOutput

        saved = await save_canon_run(
            team_id=ctx.team_id,
            user_id=ctx.user_id,
            goal=payload.prompt,
            task_type=(result.metadata or {}).get("task_type", "general"),
            four_part=FourPartOutput(**result.four_part),
            metadata=result.metadata or {},
            title=payload.title,
        )
        saved_run_id = saved.id

    return CanonExecuteResponse(
        success=True,
        four_part=result.four_part,
        metadata=result.metadata,
        saved_run_id=saved_run_id,
    )


@router.get("/runs")
async def list_canon_runs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctx: EngineContext = Depends(get_engine_context),
):
    """List the team's My Systems library (saved canon runs)."""
    return await get_team_canon_runs(team_id=ctx.team_id, limit=limit, offset=offset)


@router.get("/runs/{run_id}")
async def get_canon_run(
    run_id: str,
    ctx: EngineContext = Depends(get_engine_context),
):
    """Fetch a single saved canon run."""
    run = await get_canon_run_by_id(ctx.team_id, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Canon run not found")
    return run


@router.delete("/runs/{run_id}")
async def delete_canon_run_endpoint(
    run_id: str,
    ctx: EngineContext = Depends(get_engine_context),
):
    """Soft-delete a saved canon run. WE EVOLVE, NEVER DELETE -- the record is deactivated, not removed."""
    ctx.require_write()
    try:
        await delete_canon_run(ctx.team_id, run_id)
        return {"message": "Canon run deactivated"}
    except CanonRunError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/status")
async def canon_status(ctx: EngineContext = Depends(get_engine_context)):
    """Describe the canon contract layer: layering model and live fallback chain."""
    return {
        "contract": ["core_insight", "system_blueprint", "leverage_point", "executable_output"],
        "layers": ["ontology", "system", "mechanics", "outputs"],
        "wired_engines": sorted(CANON_ENGINE_KEYS),
        "not_yet_wired": [
            "blueprint", "anime_character", "anime_lore", "anime_story",
            "art_direction", "money_pipeline", "pipeline_composer",
        ],
        "approved_models": sorted(APPROVED_MODELS),
        "default_fallback_chain": default_fallback_chain("gpt-5.2"),
        "founding_canon_model_target": ["gpt-5.2", "claude-sonnet-4.5", "gemini-3-flash"],
        "note": (
            "Gemini is blocked by the live, tested HIC model policy "
            "(services/model_policy.py). This layer is honestly dual-model "
            "today, not tri-model, until that policy admits a third provider."
        ),
    }
