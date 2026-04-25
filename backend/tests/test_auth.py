from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.v1.auth.router import router as auth_router
from app.core.config import get_settings
from app.core.security import get_current_user, require_role
from app.schemas.auth import UserRead


JWT_SECRET = "test-supabase-jwt-secret"


@pytest.fixture(autouse=True)
def auth_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(auth_router, prefix="/api/v1/auth")

    @app.get("/admin-only", response_model=UserRead)
    async def admin_only(current_user: UserRead = Depends(require_role("admin"))) -> UserRead:
        return current_user

    return TestClient(app)


def build_token(
    *,
    role: str = "user",
    expires_delta: timedelta = timedelta(minutes=5),
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": "user-123",
        "email": "user@example.com",
        "app_role": role,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def test_get_me_returns_authenticated_user(client: TestClient) -> None:
    token = build_token(role="admin")

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "user-123",
        "email": "user@example.com",
        "role": "admin",
    }


def test_get_me_requires_authorization_header(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing Authorization header"}


def test_get_me_rejects_invalid_or_expired_token(client: TestClient) -> None:
    invalid_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    expired_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {build_token(expires_delta=timedelta(minutes=-5))}"},
    )

    assert invalid_response.status_code == 401
    assert invalid_response.json() == {"detail": "Invalid authentication token"}
    assert expired_response.status_code == 401
    assert expired_response.json() == {"detail": "Token has expired"}


def test_require_role_rejects_wrong_role(client: TestClient) -> None:
    response = client.get(
        "/admin-only",
        headers={"Authorization": f"Bearer {build_token(role='user')}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}
