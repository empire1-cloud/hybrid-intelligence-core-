"""Operator authorization for the SLA113 surface (and other operator writes).

Audit evidence (live ``app.routes`` table, Oct 2026): all 78 ``/api/sla113/*``
routes were mounted with no authentication. Anonymous callers could create and
delete tenants, change tenant credits and RTP, queue and delete jobs, write
deploy files to disk, and trigger paid LLM calls billed to EMERGENT_LLM_KEY
(``/terminal``, ``/vision/generate``, ``/logic/generate``, ``/compose``,
``/audio/generate``) and GEMINI_API_KEY (``/vision/generate-image``).

The SLA113 console has no login of its own, and the public Arcade and Investor
Showcase pages read SLA113 anonymously, so this guard is deliberately shaped:

* Reads (GET/HEAD/OPTIONS) and websockets stay public -- the Arcade and the
  Showcase depend on them -- except ``SENSITIVE_READ_PATTERNS`` (tenant
  credits/RTP), which require an operator.
* ``PUBLIC_WRITE_PATTERNS`` (the Showcase "deploy demo lobby" button) stay
  anonymous but are rate limited per client.
* Every other write requires an operator: either the ``X-SLA113-Operator-Key``
  header matching ``SLA113_OPERATOR_KEY``, or a HIC JWT whose user has
  ``system_role == "admin"``.

``SLA113_AUTH_MODE=audit`` logs would-be denials without blocking, for a staged
rollout. The default is ``enforce``.
"""

import hmac
import logging
import os
import re

from fastapi import HTTPException
from starlette.requests import HTTPConnection

from core.rate_limit import check_rate_limit, client_ip

logger = logging.getLogger(__name__)

OPERATOR_HEADER = "x-sla113-operator-key"
MIN_OPERATOR_KEY_LENGTH = 24
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

SENSITIVE_READ_PATTERNS = (
    re.compile(r"^/api/sla113/tenants/?$"),
)

# Anonymous writes that a public page depends on. Rate limited.
PUBLIC_WRITE_PATTERNS = (
    re.compile(r"^/api/sla113/lobbies/[^/]+/deploy/?$"),
)
PUBLIC_WRITE_LIMIT = int(os.environ.get("SLA113_PUBLIC_DEPLOY_LIMIT", "5"))
PUBLIC_WRITE_WINDOW_SECONDS = int(os.environ.get("SLA113_PUBLIC_DEPLOY_WINDOW", "3600"))


def _auth_mode() -> str:
    mode = os.environ.get("SLA113_AUTH_MODE", "enforce").strip().lower()
    return mode if mode in {"enforce", "audit"} else "enforce"


def _matches(patterns, path: str) -> bool:
    return any(p.match(path) for p in patterns)


def _operator_key_valid(conn: HTTPConnection) -> bool:
    configured = os.environ.get("SLA113_OPERATOR_KEY", "")
    supplied = conn.headers.get(OPERATOR_HEADER, "")
    if len(configured) < MIN_OPERATOR_KEY_LENGTH or not supplied:
        return False
    return hmac.compare_digest(configured.encode(), supplied.encode())


async def _is_system_admin(conn: HTTPConnection) -> bool:
    auth = conn.headers.get("authorization", "")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token or token.startswith("hic_"):
        # API keys are team credentials and may never act as an operator.
        return False

    from core.security import decode_token
    from database import users_collection
    from bson import ObjectId

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return False
    try:
        user = await users_collection().find_one({"_id": ObjectId(payload.get("sub"))})
    except Exception:
        return False
    return bool(user and user.get("is_active", True) and user.get("system_role") == "admin")


async def is_operator(conn: HTTPConnection) -> bool:
    return _operator_key_valid(conn) or await _is_system_admin(conn)


async def require_operator(conn: HTTPConnection) -> None:
    """Unconditional operator check (for single operator-only routes)."""
    if await is_operator(conn):
        return
    if _auth_mode() == "audit":
        logger.warning("operator_guard audit: would deny %s", conn.url.path)
        return
    raise HTTPException(
        status_code=401,
        detail={
            "code": "OPERATOR_REQUIRED",
            "message": "This action requires an SLA113 operator key or a system-admin session.",
        },
    )


async def sla113_operator_guard(conn: HTTPConnection) -> None:
    """Router-level dependency for /api/sla113 (works for HTTP and websockets)."""
    if conn.scope.get("type") == "websocket":
        return

    method = conn.scope.get("method", "GET").upper()
    path = conn.url.path

    if method in SAFE_METHODS and not _matches(SENSITIVE_READ_PATTERNS, path):
        return

    if method not in SAFE_METHODS and _matches(PUBLIC_WRITE_PATTERNS, path):
        if await is_operator(conn):
            return
        check_rate_limit(
            f"sla113-public-write:{client_ip(conn)}",
            PUBLIC_WRITE_LIMIT,
            PUBLIC_WRITE_WINDOW_SECONDS,
        )
        return

    await require_operator(conn)
