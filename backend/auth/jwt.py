"""Gamma AI — JWT Authentication."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from fastapi import Depends, HTTPException, WebSocket, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from config import Settings, get_settings

security = HTTPBearer(auto_error=False)


def create_token(
    session_id: Optional[str] = None,
    settings: Settings | None = None,
) -> tuple[str, str]:
    """Create a JWT token for the given session.

    Returns:
        Tuple of (token, session_id).
    """
    if settings is None:
        settings = get_settings()
    if session_id is None:
        session_id = str(uuid4())

    payload = {
        "sub": session_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours),
        "type": "session",
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, session_id


def validate_token(token: str, settings: Settings | None = None) -> dict:
    """Validate a JWT token and return the payload.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    if settings is None:
        settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_session(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    settings: Settings = Depends(get_settings),
) -> dict:
    """FastAPI dependency — extract and validate JWT from Authorization header.

    If no token is provided, auto-issue a new session token.
    """
    if credentials is None:
        # Auto-issue a session for MVP (no login screen)
        _token, session_id = create_token(settings=settings)
        return {"sub": session_id, "type": "session"}

    payload = validate_token(credentials.credentials, settings)
    return payload


async def validate_ws_token(websocket: WebSocket) -> dict:
    """Validate JWT from WebSocket query params or subprotocol.

    Expected: ws://host/ws/{session_id}?token=<jwt>
    """
    token = websocket.query_params.get("token")
    if not token:
        # Try to get from headers (some clients send as subprotocol)
        token = websocket.headers.get("authorization", "").replace("Bearer ", "")

    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        raise HTTPException(status_code=401, detail="Missing token")

    settings = get_settings()
    try:
        payload = validate_token(token, settings)
        return payload
    except HTTPException:
        await websocket.close(code=4001, reason="Invalid token")
        raise
