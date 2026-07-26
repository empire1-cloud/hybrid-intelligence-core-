"""Record successful HIC executions against the team's monthly allowance."""

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from services.usage_service import increment_usage


logger = logging.getLogger(__name__)


class SubscriptionUsageMiddleware(BaseHTTPMiddleware):
    """Commit usage only after an authenticated engine request succeeds."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        pending = getattr(request.state, "hic_execution_pending", False)
        context = getattr(request.state, "engine_context", None)

        if pending and context and response.status_code < 400:
            try:
                await increment_usage(
                    team_id=context.team_id,
                    executions=1,
                    api_calls=1 if context.actor_type == "api_key" else 0,
                )
            except Exception as exc:
                # Do not make the customer repeat a completed model execution.
                # The error is logged for operational reconciliation.
                logger.exception(
                    "Failed to commit HIC usage after successful execution",
                    extra={
                        "team_id": context.team_id,
                        "actor_type": context.actor_type,
                        "path": request.url.path,
                        "error": str(exc),
                    },
                )

        return response
