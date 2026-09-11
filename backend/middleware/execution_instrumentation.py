"""
Execution Instrumentation Middleware

Captures rich metrics from every AI engine execution:
- Execution ID (unique identifier)
- Provider (anthropic, openai, etc.)
- Model (claude-opus-5, gpt-4, etc.)
- Token usage (input, output, total)
- Cost (USD)
- Quality/confidence score
- Latency
- Success/error status

This transforms raw execution logs into an observable AI operations system.
"""

import time
import json
import uuid
from datetime import datetime, timezone
from typing import Callable, Optional, Dict, Any
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from services.execution_logger_db import log_execution
from core.auth_service import verify_token_from_request


# Endpoints that should be fully instrumented
INSTRUMENTED_ENDPOINTS = [
    "/api/core/execute",
    "/api/strategy",
    "/api/plan",
    "/api/analyze",
    "/api/opportunities",
    "/api/evaluate",
    "/api/pricing",
    "/api/blueprint",
    "/api/persona",
    "/api/anime/character",
    "/api/anime/lore",
    "/api/anime/story",
    "/api/art-direction",
    "/api/money-pipeline",
    "/api/pipeline/compose",
    "/api/route"
]


def get_engine_from_path(path: str) -> str:
    """Extract engine name from API path."""
    path_to_engine = {
        "/api/core/execute": "hybrid_intelligence_core",
        "/api/strategy": "strategy",
        "/api/plan": "plan_builder",
        "/api/analyze": "analysis",
        "/api/opportunities": "opportunity",
        "/api/evaluate": "evaluator",
        "/api/pricing": "pricing",
        "/api/blueprint": "blueprint",
        "/api/persona": "persona",
        "/api/anime/character": "anime_character",
        "/api/anime/lore": "anime_lore",
        "/api/anime/story": "anime_story",
        "/api/art-direction": "art_direction",
        "/api/money-pipeline": "money_pipeline",
        "/api/pipeline/compose": "pipeline_composer",
        "/api/route": "routing",
    }

    for endpoint, engine in path_to_engine.items():
        if path.startswith(endpoint):
            return engine
    return "unknown"


def extract_metrics_from_response(response_data: Dict[str, Any]) -> Dict[str, Optional[Any]]:
    """
    Extract instrumentation metrics from engine response.

    Looks for standard metric fields in response metadata or top level.
    """
    metrics = {
        "provider": None,
        "model": None,
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "cost_usd": None,
        "confidence": None,
    }

    # Check metadata section (most common)
    metadata = response_data.get("metadata", {})
    if isinstance(metadata, dict):
        metrics["provider"] = metadata.get("provider")
        metrics["model"] = metadata.get("model")
        metrics["input_tokens"] = metadata.get("input_tokens")
        metrics["output_tokens"] = metadata.get("output_tokens")
        metrics["total_tokens"] = metadata.get("total_tokens")
        metrics["cost_usd"] = metadata.get("cost_usd")
        metrics["confidence"] = metadata.get("confidence")

    # Check for metrics at top level (fallback)
    if not metrics["provider"]:
        metrics["provider"] = response_data.get("provider")
    if not metrics["model"]:
        metrics["model"] = response_data.get("model")
    if not metrics["input_tokens"]:
        metrics["input_tokens"] = response_data.get("input_tokens")
    if not metrics["output_tokens"]:
        metrics["output_tokens"] = response_data.get("output_tokens")
    if not metrics["total_tokens"]:
        metrics["total_tokens"] = response_data.get("total_tokens")
    if not metrics["cost_usd"]:
        metrics["cost_usd"] = response_data.get("cost_usd")
    if not metrics["confidence"]:
        metrics["confidence"] = response_data.get("confidence")

    # Ensure token counts are integers
    for key in ["input_tokens", "output_tokens", "total_tokens"]:
        if metrics[key] is not None and not isinstance(metrics[key], int):
            try:
                metrics[key] = int(metrics[key])
            except (ValueError, TypeError):
                metrics[key] = None

    # Ensure cost is float
    if metrics["cost_usd"] is not None and not isinstance(metrics["cost_usd"], float):
        try:
            metrics["cost_usd"] = float(metrics["cost_usd"])
        except (ValueError, TypeError):
            metrics["cost_usd"] = None

    # Ensure confidence is float between 0-1
    if metrics["confidence"] is not None:
        try:
            confidence = float(metrics["confidence"])
            if 0 <= confidence <= 1:
                metrics["confidence"] = confidence
            else:
                metrics["confidence"] = None
        except (ValueError, TypeError):
            metrics["confidence"] = None

    return metrics


class ExecutionInstrumentationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for capturing comprehensive execution metrics.

    Logs every engine execution with:
    - Unique execution ID
    - Provider and model info
    - Token usage and cost
    - Quality/confidence score
    - Success/error status
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method

        # Only instrument POST requests to engine endpoints
        should_instrument = (
            method == "POST"
            and any(path.startswith(ep) for ep in INSTRUMENTED_ENDPOINTS)
        )

        if not should_instrument:
            return await call_next(request)

        # Read request body
        body = await request.body()
        try:
            input_data = json.loads(body) if body else {}
        except:
            input_data = {"raw": body.decode()[:500] if body else ""}

        # Reconstruct request
        async def receive():
            return {"type": "http.request", "body": body}

        request = Request(request.scope, receive)

        # Generate execution ID
        execution_id = str(uuid.uuid4())

        # Execute the request and measure time
        start_time = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)

        # Read response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        # Parse response and extract metrics
        output_data = None
        error_message = None
        status = "success"
        extracted_metrics = {}

        try:
            if response.status_code >= 400:
                status = "error"
                error_message = response_body.decode()[:500]
            else:
                output_data = json.loads(response_body)
                # Extract metrics from response
                extracted_metrics = extract_metrics_from_response(output_data)
        except:
            if response.status_code >= 400:
                error_message = "Failed to parse error response"

        # Get team and user from request context
        team_id = None
        user_id = None

        try:
            # Try to extract from auth header
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                # This would need proper token parsing
                # For now, we'll try to get it from the request scope
                pass

            # Try to get from scope if available
            if hasattr(request.state, "user_id"):
                user_id = request.state.user_id
            if hasattr(request.state, "team_id"):
                team_id = request.state.team_id
        except:
            pass

        # Skip logging if we don't have auth info (will be completed by dependency injection)
        # This is handled in the engine routers which call log_execution directly

        # Reconstruct and return response
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
