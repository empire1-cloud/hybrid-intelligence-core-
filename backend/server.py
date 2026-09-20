from fastapi import FastAPI, APIRouter, Depends
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from database import connect_to_database, close_database_connection, get_database
from routers.sla113 import seed_default_pipelines, seed_default_lobbies, start_worker, stop_worker
from routers.empire1 import router as empire1_router, seed_ecosystem
from routers.empire_intake import router as empire_intake_router
from core.engine_context import enforce_engine_subscription


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_database()
    logging.info("Database connected on startup")
    await seed_default_pipelines()
    await seed_default_lobbies()
    await seed_ecosystem()
    start_worker()
    logging.info("Night Queue Worker started")
    yield
    stop_worker()
    await close_database_connection()
    logging.info("Database connection closed on shutdown")


app = FastAPI(
    title="Empire-1 Hybrid Intelligence Core",
    description="Empire-1 hosted multi-model intelligence and execution core using approved non-Google providers.",
    version="2.2.0",
    lifespan=lifespan,
)

api_router = APIRouter(prefix="/api")

from routers.auth import router as auth_router
from routers.teams import router as teams_router
from routers.profile import router as profile_router
from routers.invites import router as invites_router
from routers.billing import router as billing_router
from routers.api_keys import router as api_keys_router
from routers.admin import router as admin_router
from routers.system import router as system_router
from routers.execution_analytics import router as execution_analytics_router

from routers.engines import (
    core_router,
    strategy_router,
    drift_router,
    plan_router,
    analysis_router,
    opportunity_router,
    evaluator_router,
    pricing_router,
    blueprint_router,
    persona_router,
    pipeline_router,
    anime_character_router,
    anime_lore_router,
    anime_story_router,
    art_direction_router,
    money_pipeline_router,
    analytics_router,
    discovery_router,
)
from routers.engines.history_protected import router as history_protected_router
from routers.pipelines import router as pipelines_router
from routers.sla113 import router as sla113_router
from routes.startup_copilot_routes import router as startup_copilot_router
from routers.genesis import router as genesis_router

api_router.include_router(auth_router)
api_router.include_router(teams_router)
api_router.include_router(profile_router)
api_router.include_router(invites_router)
api_router.include_router(billing_router)
api_router.include_router(api_keys_router)
api_router.include_router(admin_router)
api_router.include_router(system_router)
api_router.include_router(empire_intake_router)
api_router.include_router(execution_analytics_router)

api_router.include_router(history_protected_router)
api_router.include_router(pipelines_router)

# Executable Empire-1 HIC engine surfaces require a JWT workspace or valid hic_ API key.
# The dependency checks the monthly allowance before execution; successful usage
# is committed by SubscriptionUsageMiddleware after the route returns.
engine_dependencies = [Depends(enforce_engine_subscription)]
api_router.include_router(core_router, dependencies=engine_dependencies)
api_router.include_router(strategy_router, dependencies=engine_dependencies)
api_router.include_router(drift_router, dependencies=engine_dependencies)
api_router.include_router(plan_router, dependencies=engine_dependencies)
api_router.include_router(analysis_router, dependencies=engine_dependencies)
api_router.include_router(opportunity_router, dependencies=engine_dependencies)
api_router.include_router(evaluator_router, dependencies=engine_dependencies)
api_router.include_router(pricing_router, dependencies=engine_dependencies)
api_router.include_router(blueprint_router, dependencies=engine_dependencies)
api_router.include_router(persona_router, dependencies=engine_dependencies)
api_router.include_router(pipeline_router, dependencies=engine_dependencies)
api_router.include_router(anime_character_router, dependencies=engine_dependencies)
api_router.include_router(anime_lore_router, dependencies=engine_dependencies)
api_router.include_router(anime_story_router, dependencies=engine_dependencies)
api_router.include_router(art_direction_router, dependencies=engine_dependencies)
api_router.include_router(money_pipeline_router, dependencies=engine_dependencies)

# Existing analytics transport remains read-only/public in this release so its
# polling and WebSocket dashboard are not broken by the execution gate.
api_router.include_router(analytics_router)

# Engine Discovery (read-only, public) — No subscription required
# Exposes engine contracts, orchestration metadata, and system information
api_router.include_router(discovery_router)

# SLA113 is Empire-1's deeper tenant, policy, operator, and product-factory layer.
# It remains commercially distinct without being separated from the Empire-1 parent.
api_router.include_router(sla113_router)

# Startup Copilot: 12 founder skills for idea validation through scaling
# Includes chained workflows for multi-skill founder guidance
api_router.include_router(startup_copilot_router, dependencies=engine_dependencies)

# Genesis Engine: end-to-end game specification -> assets -> deterministic math ->
# verification -> playable web composition -> packaged build artifact.
api_router.include_router(genesis_router)


class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


@api_router.get("/")
async def root():
    return {
        "parent": "Empire-1",
        "product": "Hybrid Intelligence Core",
        "version": "2.2.0",
        "billing": "monthly_cancel_anytime",
        "model_policy": "approved_non_google_only",
        "canon": "WE EVOLVE. NEVER DELETE.",
    }


@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "parent": "Empire-1",
        "product": "Hybrid Intelligence Core",
        "version": "2.2.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    db = get_database()
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    db = get_database()
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)

    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])

    return status_checks


app.include_router(api_router)
app.include_router(empire1_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

from middleware.model_policy_middleware import ModelPolicyMiddleware
from middleware.subscription_usage_middleware import SubscriptionUsageMiddleware
from middleware.logging_middleware import ExecutionLoggingMiddleware

app.add_middleware(ModelPolicyMiddleware)
app.add_middleware(ExecutionLoggingMiddleware)
app.add_middleware(SubscriptionUsageMiddleware)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.get("/api/empire1/status")
async def empire1_status():
    return {
        "universe": "empire1",
        "status": "online",
        "description": "Empire-1 Hybrid Intelligence Core — 19 AI Engines",
        "product": "Empire-1 Hybrid Intelligence SaaS",
        "billing": "monthly_cancel_anytime",
        "hic_is_inside_empire1": True,
    }


@app.get("/api/southern/status")
async def southern_status():
    return {
        "universe": "southern",
        "status": "online",
        "description": "Southern Lyfestyle Game OS",
        "product": "Southern Game OS",
        "parent": "Empire-1",
    }


@app.get("/api/soulfire/status")
async def soulfire_status():
    return {
        "universe": "soulfire",
        "status": "online",
        "description": "Soulfire Ecosystem Blueprint (ASW, El Coro, Sentinel, SL Universal)",
        "product": "Lyrica 3 Pro — AI Music Creation",
        "engine": "Empire-1 approved provider stack",
        "parent": "Empire-1",
    }
