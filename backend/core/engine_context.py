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
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.dependencies import get_current_user, get_current_team
from database import teams_collection
from services.api_key_service import get_api_key_context
from services.execution_logger_db import log_execution
from services.usage_service import check_usage_limit


engine_security = HTTPBearer(auto_error=False)

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
        permissions: Optional[list[str]] = None,
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
        self.permissions = set(permissions or [])

    @property
    def can_write(self) -> bool:
        if self.actor_type == "api_key":
            return "execute" in self.permissions
        return self.user_role in ["owner", "admin", "member"]

    @property
    def can_admin(self) -> bool:
        if self.actor_type == "api_key":
            return False
        return self.user_role in ["owner", "admin"]

    @property
    def can_read(self) -> bool:
        if self.actor_type == "api_key":
            return bool({"read", "execute"} & self.permissions)
        return self.user_role in ["owner", "admin", "member", "viewer"]

    def require_read(self):
        if not self.can_read:
            raise HTTPException(status_code=403, detail="This actor does not have read access")

    def require_write(self):
        if not self.can_write:
            raise HTTPException(status_code=403, detail="This actor does not have engine execution access")

    def require_admin(self):
        if not self.can_admin:
            raise HTTPException(status_code=403, detail="A user with admin or owner role is required")


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
    # Role is retained only as team metadata. API-key capabilities are decided
    # by the key permission set and can never administer the workspace.
    team["user_role"] = "member"

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
        permissions=api_context.get("permissions", []),
    )


async def get_engine_context(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(engine_security),
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
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(engine_security),
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


def extract_execution_metrics(output_data: Optional[dict]) -> dict:
    """Pull provider/model/token/cost/confidence off an engine result.

    Engines report these under `metadata`; a bare top-level key is accepted as a
    fallback. Anything missing or malformed stays None so the execution still
    logs rather than failing on its own instrumentation.
    """
    metrics = {
        "provider": None,
        "model": None,
        "input_tokens": None,
        "output_tokens": None,
        "cost_usd": None,
        "confidence": None,
    }
    if not isinstance(output_data, dict):
        return metrics

    metadata = output_data.get("metadata")
    metadata = metadata if isinstance(metadata, dict) else {}

    for key in metrics:
        value = metadata.get(key, output_data.get(key))
        if value is None:
            continue
        if key in ("input_tokens", "output_tokens"):
            try:
                metrics[key] = int(value)
            except (TypeError, ValueError):
                continue
        elif key == "confidence":
            try:
                confidence = float(value)
            except (TypeError, ValueError):
                continue
            if 0.0 <= confidence <= 1.0:
                metrics[key] = confidence
        elif key == "cost_usd":
            try:
                metrics[key] = float(value)
            except (TypeError, ValueError):
                continue
        else:
            metrics[key] = str(value)

    return metrics


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
    """Log an engine execution with team, actor, and instrumentation context."""
    metrics = extract_execution_metrics(output_data)

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
        **metrics,
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
