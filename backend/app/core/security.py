from collections.abc import Callable
from functools import lru_cache
from typing import Any, Optional

import jwt
from fastapi import Depends, Header, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWKClient
from jwt.exceptions import PyJWKClientError
from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.auth import UserRead


@lru_cache(maxsize=1)
def _get_jwks_client() -> PyJWKClient:
    settings = get_settings()
    return PyJWKClient(
        f"{settings.supabase_url}/auth/v1/.well-known/jwks.json",
        lifespan=3600,
    )


def verify_jwt(token: str) -> dict[str, Any]:
    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
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
    except PyJWKClientError as exc:
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


async def get_current_user(authorization: Optional[str] = Header(default=None)) -> UserRead:
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

    raw_role = payload.get("app_role") or payload.get("app_metadata", {}).get("app_role")
    if raw_role is None:
        raw_role = "user" if payload.get("role") == "authenticated" else None

    try:
        return UserRead(
            id=str(payload["sub"]),
            email=payload["email"],
            role=raw_role,
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
