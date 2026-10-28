"""CORS settings resolution.

HIC authenticates with bearer tokens (JWT or ``hic_`` API keys) held by the
client, never with cookies, so cross-origin credentials are not required for
the app to work. The old configuration paired ``allow_origins=["*"]`` (the
default when CORS_ORIGINS is unset) with ``allow_credentials=True``; Starlette
answers that combination by echoing any requesting origin for credentialed
requests, which is the permissive behaviour browsers' wildcard rule exists to
prevent.

Rules:
- Explicit origin list -> credentials allowed for exactly those origins.
- Wildcard / unset      -> any origin, but credentials are never allowed.
"""

import logging
import os
from typing import Dict, List

from core.security import is_production

logger = logging.getLogger(__name__)


def _parse_origins(raw: str) -> List[str]:
    return [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]


def resolve_cors_settings() -> Dict[str, object]:
    origins = _parse_origins(os.environ.get("CORS_ORIGINS", ""))
    wildcard = not origins or "*" in origins

    if wildcard:
        if is_production():
            logger.warning(
                "CORS_ORIGINS is unset or '*' in production. Allowing any origin "
                "WITHOUT credentials. Set CORS_ORIGINS to your frontend origin(s)."
            )
        return {
            "allow_origins": ["*"],
            "allow_credentials": False,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }

    return {
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
