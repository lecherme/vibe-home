from datetime import datetime, timedelta, timezone
import importlib

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings


JWT_SECRET = "test-supabase-jwt-secret"


@pytest.fixture(autouse=True)
def auth_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("RATE_LIMIT_AUTH", "2/minute")
    get_settings.cache_clear()

    yield

    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    import app.api.v1.auth.router as auth_router_module
    import app.main as main_module

    auth_router_module = importlib.reload(auth_router_module)
    auth_router_module.auth_rate_limiter.reset()
    main_module = importlib.reload(main_module)

    return TestClient(main_module.app)


def build_token(
    *,
    role: str = "user",
    expires_delta: timedelta = timedelta(minutes=5),
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "user-123",
        "email": "user@example.com",
        "app_role": role,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def test_get_auth_me_returns_429_after_rate_limit_is_exceeded(client: TestClient) -> None:
    headers = {"Authorization": f"Bearer {build_token()}"}

    first_response = client.get("/api/v1/auth/me", headers=headers)
    second_response = client.get("/api/v1/auth/me", headers=headers)
    third_response = client.get("/api/v1/auth/me", headers=headers)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert third_response.status_code == 429
    assert third_response.json() == {"detail": "Rate limit exceeded"}
