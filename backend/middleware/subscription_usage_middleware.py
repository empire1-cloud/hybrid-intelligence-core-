"""Record successful HIC executions against the team's monthly allowance."""

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from services.usage_service import increment_usage, release_execution


logger = logging.getLogger(__name__)


class SubscriptionUsageMiddleware(BaseHTTPMiddleware):
    """Commit usage only after an authenticated engine request succeeds."""

    @staticmethod
    async def _release_if_reserved(request: Request) -> None:
        context = getattr(request.state, "engine_context", None)
        if not (
            context
            and getattr(request.state, "hic_execution_pending", False)
            and getattr(request.state, "hic_execution_reserved", False)
        ):
            return
        try:
            await release_execution(context.team_id, 1)
        except Exception as exc:
            logger.exception(
                "Failed to release reserved HIC execution slot after an unhandled error",
                extra={"team_id": context.team_id, "path": request.url.path, "error": str(exc)},
            )

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception:
            # call_next re-raises an exception the route let escape, so the
            # >=400 branch below never sees it. Give the reserved slot back
            # before propagating, or repeated failures would exhaust the plan.
            await self._release_if_reserved(request)
            raise

        pending = getattr(request.state, "hic_execution_pending", False)
        reserved = getattr(request.state, "hic_execution_reserved", False)
        context = getattr(request.state, "engine_context", None)

        if pending and context and reserved and response.status_code >= 400:
            # The slot was claimed up front; a failed execution gives it back.
            try:
                await release_execution(context.team_id, 1)
            except Exception as exc:
                logger.exception(
                    "Failed to release reserved HIC execution slot",
                    extra={"team_id": context.team_id, "path": request.url.path, "error": str(exc)},
                )
        elif pending and context and response.status_code < 400:
            try:
                await increment_usage(
                    team_id=context.team_id,
                    # Already counted at reservation time; only API-call
                    # attribution remains to be recorded.
                    executions=0 if reserved else 1,
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
