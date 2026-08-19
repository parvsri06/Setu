"""Auth endpoint (Phase 6): exchange the shared DEV_API_KEY for a JWT.

Design A (Ed25519 device signing) was dropped — there is no responders/device
table. "Admins = us", so this is a lightweight dev token, not a full IdP.
The export/admin routers also accept the raw X-Dev-Key header directly.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..config import DEV_API_KEY
from ..schemas import LoginRequest, TokenResponse
from ..security import create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    if not payload.api_key or payload.api_key != DEV_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "unauthorized", "message": "invalid api key"}},
        )
    token, expires_in = create_access_token(subject="dev", role="admin")
    return TokenResponse(token=token, expiresIn=expires_in, role="admin")
