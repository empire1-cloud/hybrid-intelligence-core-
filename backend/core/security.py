"""
Core security utilities: password hashing, JWT tokens, etc.
"""

import logging
import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
import bcrypt
import jwt
from pydantic import BaseModel


PRODUCTION_ENV_NAMES = {"production", "prod"}
MIN_JWT_SECRET_LENGTH = 32


def is_production() -> bool:
    """True when APP_ENV names a production deployment."""
    return os.environ.get("APP_ENV", "development").strip().lower() in PRODUCTION_ENV_NAMES


def _load_jwt_secret() -> str:
    """Return the configured JWT secret, failing closed in production.

    The previous behaviour generated a random secret whenever JWT_SECRET_KEY
    was missing. Under the shipped systemd unit (4 gunicorn workers, recycled
    every 1000 requests) every worker invented its own secret, so a token
    signed by one worker was rejected by the other three and every session
    died on recycle. Production now refuses to start instead.
    """
    secret = os.environ.get("JWT_SECRET_KEY", "").strip()
    if secret:
        if is_production() and len(secret) < MIN_JWT_SECRET_LENGTH:
            raise RuntimeError(
                f"JWT_SECRET_KEY must be at least {MIN_JWT_SECRET_LENGTH} characters in production."
            )
        return secret

    if is_production():
        raise RuntimeError(
            "JWT_SECRET_KEY is not set. Refusing to start in production with an "
            "ephemeral per-process signing key."
        )

    logging.getLogger(__name__).warning(
        "JWT_SECRET_KEY not set; using an ephemeral development key. Tokens will "
        "not survive a restart and are not shared across workers."
    )
    return secrets.token_urlsafe(32)


# JWT Configuration
JWT_SECRET_KEY = _load_jwt_secret()
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: str  # user_id
    type: str  # "access" or "refresh"
    exp: datetime
    iat: datetime
    jti: Optional[str] = None  # JWT ID for refresh token tracking


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(user_id: str, additional_claims: Dict[str, Any] = None) -> str:
    """Create a short-lived access token."""
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": user_id,
        "type": "access",
        "iat": now,
        "exp": expires,
    }
    
    if additional_claims:
        payload.update(additional_claims)
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> Tuple[str, str]:
    """
    Create a long-lived refresh token.
    Returns: (token, token_hash) - store the hash, return the token to user
    """
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    jti = secrets.token_urlsafe(32)
    
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": expires,
        "jti": jti,
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    token_hash = hash_token(token)
    
    return token, token_hash


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def hash_token(token: str) -> str:
    """Hash a token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_invite_token() -> Tuple[str, str]:
    """Generate a secure invite token. Returns (token, token_hash)."""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash


def generate_reset_token() -> Tuple[str, str]:
    """Generate a password reset token. Returns (token, token_hash)."""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash


def generate_slug(name: str) -> str:
    """Generate a URL-safe slug from a name."""
    import re
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower())
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Add random suffix for uniqueness
    suffix = secrets.token_hex(4)
    return f"{slug}-{suffix}"


def get_token_expiry_seconds() -> int:
    """Get access token expiry in seconds."""
    return ACCESS_TOKEN_EXPIRE_MINUTES * 60


def get_refresh_token_expiry() -> datetime:
    """Get refresh token expiry datetime."""
    return datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
