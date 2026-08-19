"""Security helpers: JWT issuance/verification, dev-key gating, Aadhaar masking."""
from __future__ import annotations

import datetime
from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    DEV_API_KEY,
    JWT_ALGORITHM,
    JWT_SECRET,
)

_credentials_scheme = HTTPBearer(auto_error=False)


def create_access_token(subject: str, role: str = "admin") -> tuple[str, int]:
    """Return (token, expires_in_seconds)."""
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "role": role, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, ACCESS_TOKEN_EXPIRE_MINUTES * 60


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def mask_aadhaar(aadhaar: str) -> str:
    """Mask all but the last 4 digits: 123456789012 -> XXXX-XXXX-9012."""
    last4 = aadhaar[-4:] if len(aadhaar) >= 4 else aadhaar
    return f"XXXX-XXXX-{last4}"


def require_dev(
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(_credentials_scheme),
    x_dev_key: Optional[str] = Header(default=None, alias="X-Dev-Key"),
) -> str:
    """Gate export/admin endpoints.

    Accepts either a valid JWT (issued by /api/v1/auth/login) or the shared
    DEV_API_KEY passed as the ``X-Dev-Key`` header. "Admins = us", so this is
    intentionally lightweight — no user/role table.
    """
    if x_dev_key and x_dev_key == DEV_API_KEY:
        return "dev-key"
    if bearer and bearer.credentials:
        try:
            payload = decode_access_token(bearer.credentials)
            return payload.get("sub", "dev")
        except jwt.PyJWTError:
            pass
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": {
                "code": "forbidden",
                "message": "Export/admin access requires a valid dev token or X-Dev-Key header",
            }
        },
    )
