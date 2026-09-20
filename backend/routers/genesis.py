"""Genesis Engine API: one request executes the complete generation pipeline."""
from fastapi import APIRouter, HTTPException
from . import __init__
from genesis_engine.models import GenerateRequest, GenerateResponse, GameSpec
from genesis_engine.pipeline import GenesisPipeline

router=APIRouter(prefix="/genesis",tags=["Genesis Engine"])
_pipeline=GenesisPipeline()

@router.get("/status")
async def genesis_status():
    return {"status":"online","engine":"Genesis Engine","pipeline":["SPECIFIED","GENERATED","CALCULATED","VERIFIED","COMPOSED","PACKAGED"],"math":"deterministic","regulatory_certification":False}

@router.post("/generate",response_model=GenerateResponse)
async def genesis_generate(request: GenerateRequest):
    try:
        result=_pipeline.run(request.spec,request.include_audio,request.include_vision,request.include_build)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500,detail=f"Genesis generation failed: {exc}") from exc

@router.post("/verify")
async def genesis_verify(spec: GameSpec):
    from genesis_engine.logic import verify_math
    return verify_math(spec)
