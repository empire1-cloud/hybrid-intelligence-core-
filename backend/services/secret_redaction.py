"""Scrub credentials out of text before it leaves the process.

Evidence this is needed: ``backend/execution_logs.json`` (committed to a public
repository) contains provider error strings of the form
``...generateContent?key=sk-emergent-...``. The upstream client embeds the API
key in the request URL, the exception message carries that URL, and 35 call
sites return ``str(e)`` to the caller. This module is applied at the shared
choke points (the global HTTPException handler, ``ErrorHandler``, and both
execution loggers) rather than at each call site.
"""

import os
import re
from typing import Any

REDACTED = "[REDACTED]"

# Environment variables whose literal values must never be echoed.
SECRET_ENV_VARS = (
    "EMERGENT_LLM_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "JWT_SECRET_KEY",
    "MONGO_URL",
    "RESEND_API_KEY",
    "SLA113_OPERATOR_KEY",
    "GITHUB_CLIENT_SECRET",
    "GOOGLE_CLIENT_SECRET",
)

_PATTERNS = [
    # key=..., api_key=..., token=... in URLs and query strings
    (re.compile(r"(?i)\b((?:api[_-]?)?key|token|secret|access_token|password)=([^&\s'\"\\]+)"), r"\1=" + REDACTED),
    # Bearer tokens
    (re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]{8,}"), r"\1 " + REDACTED),
    # Well-known key shapes
    (re.compile(r"\bsk-(?:emergent|ant|proj|live|test)?[-_]?[A-Za-z0-9_-]{12,}"), REDACTED),
    (re.compile(r"\b(?:sk|rk|pk)_(?:live|test)_[A-Za-z0-9]{10,}"), REDACTED),
    (re.compile(r"\bwhsec_[A-Za-z0-9]{10,}"), REDACTED),
    (re.compile(r"\bhic_[A-Za-z0-9_-]{16,}"), REDACTED),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{30,}"), REDACTED),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"), REDACTED),
    # Credentials inside connection strings: scheme://user:pass@host
    (re.compile(r"([a-z][a-z0-9+.-]*://[^:/\s@]+):[^@/\s]+@", re.I), r"\1:" + REDACTED + "@"),
]

_MIN_LITERAL_LENGTH = 8


def redact_secrets(text: Any) -> Any:
    """Return ``text`` with credentials replaced. Non-strings pass through."""
    if not isinstance(text, str) or not text:
        return text

    for name in SECRET_ENV_VARS:
        value = os.environ.get(name)
        if value and len(value) >= _MIN_LITERAL_LENGTH and value in text:
            text = text.replace(value, REDACTED)

    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def redact_obj(value: Any, _depth: int = 0) -> Any:
    """Recursively redact strings inside dicts/lists (bounded depth)."""
    if _depth > 8:
        return value
    if isinstance(value, str):
        return redact_secrets(value)
    if isinstance(value, dict):
        return {k: redact_obj(v, _depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_obj(v, _depth + 1) for v in value]
    if isinstance(value, tuple):
        return tuple(redact_obj(v, _depth + 1) for v in value)
    return value
