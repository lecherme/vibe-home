from collections.abc import Callable
from typing import Any

import jwt
from fastapi import Depends, Header, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.auth import UserRead


def verify_jwt(token: str) -> dict[str, Any]:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
        )
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from exc
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from exc

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    return payload


async def get_current_user(authorization: str | None = Header(default=None)) -> UserRead:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header",
        )

    payload = verify_jwt(token)

    try:
        return UserRead(
            id=str(payload["sub"]),
            email=payload["email"],
            role=payload["app_role"],
        )
    except (KeyError, TypeError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from exc


def require_role(role: str) -> Callable[..., UserRead]:
    async def role_dependency(current_user: UserRead = Depends(get_current_user)) -> UserRead:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_dependency
