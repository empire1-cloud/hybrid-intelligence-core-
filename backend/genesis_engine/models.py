"""Typed contracts for Genesis Engine generation jobs."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class GameSpec(BaseModel):
    name: str = "Genesis Game"
    game_type: str = "fish_shooter"
    theme: str = "Southern Aztec arcade"
    target_platform: str = "web"
    width: int = Field(default=1280, ge=320, le=4096)
    height: int = Field(default=720, ge=240, le=4096)
    fps: int = Field(default=60, ge=30, le=120)
    fish_count: int = Field(default=8, ge=1, le=100)
    paytable: Dict[str, float] = Field(default_factory=lambda: {
        "small": 0.25, "medium": 0.75, "large": 2.0, "boss": 8.0
    })
    target_rtp: float = Field(default=0.965, gt=0.0, lt=1.0)
    shots_per_round: int = Field(default=10000, ge=100, le=2_000_000)
    seed: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GenerateRequest(BaseModel):
    spec: GameSpec = Field(default_factory=GameSpec)
    include_audio: bool = True
    include_vision: bool = True
    include_build: bool = True

class GenerateResponse(BaseModel):
    job_id: str
    status: str
    manifest: Dict[str, Any]
    verification: Dict[str, Any]
    artifacts: List[Dict[str, Any]]
