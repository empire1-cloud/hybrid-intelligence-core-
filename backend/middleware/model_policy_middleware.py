"""API boundary enforcement for the Empire-1 HIC model policy."""

import json

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from services.model_policy import APPROVED_MODELS, BLOCKED_MODEL_TOKENS


MODEL_FIELDS = ("model", "force_model")


class ModelPolicyMiddleware(BaseHTTPMiddleware):
    """Fail closed when an API execution asks HIC to use a blocked model.

    Only top-level execution override fields are inspected. Customer content may
    legitimately contain nested business or data fields named ``model`` and
    must never be mistaken for a provider override.
    """

    async def dispatch(self, request: Request, call_next):
        if request.method not in {"POST", "PUT", "PATCH"} or not request.url.path.startswith("/api/"):
            return await call_next(request)

        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type.lower():
            return await call_next(request)

        raw_body = await request.body()
        if not raw_body:
            return await call_next(request)

        try:
            payload = json.loads(raw_body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return await call_next(request)

        if isinstance(payload, dict):
            for field in MODEL_FIELDS:
                model_value = payload.get(field)
                if not isinstance(model_value, str):
                    continue

                candidate = model_value.strip().lower()
                if any(token in candidate for token in BLOCKED_MODEL_TOKENS):
                    return JSONResponse(
                        status_code=400,
                        content={
                            "detail": "Google/Gemini models are not permitted in the Empire-1 HIC stack.",
                            "code": "MODEL_POLICY_BLOCKED",
                        },
                    )

                if candidate not in APPROVED_MODELS:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "detail": f"Model is not approved for HIC execution: {candidate}",
                            "code": "MODEL_POLICY_UNAPPROVED",
                        },
                    )

        async def receive():
            return {"type": "http.request", "body": raw_body, "more_body": False}

        request._receive = receive
        return await call_next(request)
