"""
Engine execution context with JWT or HIC API-key authentication.

This module is the subscription gate for hosted HIC engine calls. Public health
checks remain public; executable engine routes require a valid team context and
must fit inside the team's monthly execution allowance.
"""

import time
from typing import Optional

from bson import ObjectId
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from core.dependencies import security, get_current_user, get_current_team
from database import teams_collection
from services.api_key_service import get_api_key_context
from services.execution_logger_db import log_execution
from services.usage_service import check_usage_limit


PUBLIC_ENGINE_PATHS = {
    "/api/health",
    "/api/core/status",
}


class EngineContext:
    """Authenticated actor and team context for an engine execution."""

    def __init__(
        self,
        user: dict,
        team: dict,
        request: Request,
        actor_type: str = "user",
        api_key_id: Optional[str] = None,
        api_key_name: Optional[str] = None,
    ):
        self.user = user
        self.team = team
        self.request = request
        self.user_id = str(user.get("_id") or user.get("id") or user.get("user_id"))
        self.team_id = str(team.get("_id") or team.get("id") or team.get("team_id"))
        self.user_role = team.get("user_role", "member")
        self.actor_type = actor_type
        self.api_key_id = api_key_id
        self.api_key_name = api_key_name

    @property
    def can_write(self) -> bool:
        return self.user_role in ["owner", "admin", "member"]

    @property
    def can_admin(self) -> bool:
        return self.user_role in ["owner", "admin"]

    @property
    def can_read(self) -> bool:
        return self.user_role in ["owner", "admin", "member", "viewer"]

    def require_read(self):
        if not self.can_read:
            raise HTTPException(status_code=403, detail="You don't have access to view this resource")

    def require_write(self):
        if not self.can_write:
            raise HTTPException(status_code=403, detail="You need member, admin, or owner role to perform this action")

    def require_admin(self):
        if not self.can_admin:
            raise HTTPException(status_code=403, detail="You need admin or owner role to perform this action")


async def _context_from_api_key(request: Request, token: str) -> Optional[EngineContext]:
    api_context = await get_api_key_context(token)
    if not api_context:
        return None

    team_id = str(api_context["team_id"])
    if not ObjectId.is_valid(team_id):
        return None

    team = await teams_collection().find_one({
        "_id": ObjectId(team_id),
        "is_active": True,
    })
    if not team:
        return None

    team["_id"] = str(team["_id"])
    team["user_role"] = "owner"

    user = {
        "_id": str(api_context.get("user_id")),
        "email": api_context.get("user_email"),
    }

    return EngineContext(
        user=user,
        team=team,
        request=request,
        actor_type="api_key",
        api_key_id=api_context.get("api_key_id"),
        api_key_name=api_context.get("api_key_name"),
    )


async def get_engine_context(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> EngineContext:
    """Resolve a HIC engine actor from a JWT or a `hic_...` API key."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Engine execution requires a HIC account or API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    if token.startswith("hic_"):
        context = await _context_from_api_key(request, token)
        if context:
            return context
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked HIC API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_current_user(credentials)
    team = await get_current_team(request, user)
    return EngineContext(user=user, team=team, request=request, actor_type="user")


async def enforce_engine_subscription(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[EngineContext]:
    """Authenticate engine routes and reserve a valid monthly execution slot."""
    if request.method == "GET" and request.url.path in PUBLIC_ENGINE_PATHS:
        return None

    context = await get_engine_context(request, credentials)
    context.require_read()

    is_execution = request.method in {"POST", "PUT", "PATCH"}
    if is_execution:
        context.require_write()
        await check_usage_limit(context.team_id, "executions", 1)
        request.state.hic_execution_pending = True

    request.state.engine_context = context
    return context


async def log_engine_call(
    ctx: EngineContext,
    engine: str,
    input_data: dict,
    output_data: Optional[dict] = None,
    error_message: Optional[str] = None,
    duration_ms: int = 0,
    source: str = "api",
    pipeline_id: Optional[str] = None,
):
    """Log an engine execution with team and actor context."""
    await log_execution(
        team_id=ctx.team_id,
        user_id=ctx.user_id,
        engine=engine,
        input_data=input_data,
        output_data=output_data,
        error_message=error_message,
        duration_ms=duration_ms,
        source=source,
        pipeline_id=pipeline_id,
        endpoint=str(ctx.request.url.path),
        method=ctx.request.method,
    )


class EngineExecutor:
    """Async execution wrapper with team-scoped logging."""

    def __init__(
        self,
        ctx: EngineContext,
        engine: str,
        input_data: dict,
        source: str = "api",
        pipeline_id: Optional[str] = None,
    ):
        self.ctx = ctx
        self.engine = engine
        self.input_data = input_data
        self.source = source
        self.pipeline_id = pipeline_id
        self.output_data = None
        self.error_message = None
        self.start_time = None

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((time.time() - self.start_time) * 1000)
        if exc_val:
            self.error_message = str(exc_val)

        await log_engine_call(
            ctx=self.ctx,
            engine=self.engine,
            input_data=self.input_data,
            output_data=self.output_data,
            error_message=self.error_message,
            duration_ms=duration_ms,
            source=self.source,
            pipeline_id=self.pipeline_id,
        )
        return False

    def set_output(self, output: dict):
        self.output_data = output
