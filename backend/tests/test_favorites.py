from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.favorites.router import router as favorites_router
from app.core.config import get_settings
from app.core.supabase import seed_fake_supabase
from app.data.properties import get_all
from app.services.favorites.service import (
    add_favorite,
    favorites_store,
    get_user_favorites,
    is_favorite,
    remove_favorite,
)


JWT_SECRET = "test-supabase-jwt-secret"


@pytest.fixture(autouse=True)
def test_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    get_settings.cache_clear()
    seed_fake_supabase()
    yield
    seed_fake_supabase()


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(favorites_router, prefix="/api/v1/favorites")
    return TestClient(app)


def build_token(
    *,
    user_id: str = "user-123",
    email: str = "user@example.com",
    role: str = "user",
    expires_delta: timedelta = timedelta(minutes=5),
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "app_role": role,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def auth_headers(*, user_id: str = "user-123", role: str = "user") -> dict[str, str]:
    return {"Authorization": f"Bearer {build_token(user_id=user_id, role=role)}"}


def favorite_property_ids(count: int = 3) -> list[str]:
    sorted_properties = sorted(
        get_all(),
        key=lambda property_item: property_item.created_at,
        reverse=True,
    )
    return [property_item.id for property_item in sorted_properties[:count]]


def serialize_property(property_id: str) -> dict[str, object]:
    property_item = next(
        property_item for property_item in get_all() if property_item.id == property_id
    )
    return property_item.model_dump(mode="json")


def test_add_favorite_marks_property_as_favorited() -> None:
    property_id = favorite_property_ids(1)[0]

    favorite = add_favorite("user-123", property_id)

    assert favorite.property_id == property_id
    assert favorite.user_id == "user-123"
    assert is_favorite("user-123", property_id) is True


def test_remove_favorite_clears_property() -> None:
    property_id = favorite_property_ids(1)[0]
    add_favorite("user-123", property_id)

    remove_favorite("user-123", property_id)

    assert is_favorite("user-123", property_id) is False
    assert favorites_store == {}


def test_add_favorite_rejects_unknown_property() -> None:
    with pytest.raises(HTTPException) as exc_info:
        add_favorite("user-123", "does-not-exist")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Property not found"


def test_remove_favorite_rejects_missing_favorite() -> None:
    with pytest.raises(HTTPException) as exc_info:
        remove_favorite("user-123", favorite_property_ids(1)[0])

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Favorite not found"


def test_get_user_favorites_returns_paginated_results() -> None:
    property_ids = favorite_property_ids(3)
    for property_id in property_ids:
        add_favorite("user-123", property_id)

    favorite_page = get_user_favorites("user-123", page=1, page_size=2)

    assert favorite_page.total == 3
    assert [property_item.id for property_item in favorite_page.items] == property_ids[:2]


def test_post_adds_favorite_and_returns_201(client: TestClient) -> None:
    property_id = favorite_property_ids(1)[0]

    response = client.post(
        f"/api/v1/favorites/{property_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 201
    assert response.json()["property_id"] == property_id
    assert response.json()["user_id"] == "user-123"
    assert is_favorite("user-123", property_id) is True


def test_post_duplicate_returns_409(client: TestClient) -> None:
    property_id = favorite_property_ids(1)[0]
    add_favorite("user-123", property_id)

    response = client.post(
        f"/api/v1/favorites/{property_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Property already favorited"}


def test_delete_removes_favorite_and_returns_204(client: TestClient) -> None:
    property_id = favorite_property_ids(1)[0]
    add_favorite("user-123", property_id)

    response = client.delete(
        f"/api/v1/favorites/{property_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 204
    assert response.content == b""
    assert is_favorite("user-123", property_id) is False


def test_get_returns_only_current_users_favorites(client: TestClient) -> None:
    property_ids = favorite_property_ids(3)
    add_favorite("user-123", property_ids[0])
    add_favorite("user-123", property_ids[1])
    add_favorite("user-999", property_ids[2])

    response = client.get(
        "/api/v1/favorites",
        headers=auth_headers(user_id="user-123"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            serialize_property(property_id)
            for property_id in property_ids[:2]
        ],
        "total": 2,
    }


def test_get_favorite_status_returns_true_when_favorited(client: TestClient) -> None:
    property_id = favorite_property_ids(1)[0]
    add_favorite("user-123", property_id)

    response = client.get(
        f"/api/v1/favorites/{property_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == {"is_favorite": True}


def test_get_favorite_status_returns_false_when_not_favorited(
    client: TestClient,
) -> None:
    property_id = favorite_property_ids(1)[0]

    response = client.get(
        f"/api/v1/favorites/{property_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == {"is_favorite": False}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/api/v1/favorites"),
        ("get", f"/api/v1/favorites/{favorite_property_ids(1)[0]}"),
        ("post", f"/api/v1/favorites/{favorite_property_ids(1)[0]}"),
        ("delete", f"/api/v1/favorites/{favorite_property_ids(1)[0]}"),
    ],
)
def test_favorites_endpoints_require_authorization(
    client: TestClient,
    method: str,
    path: str,
) -> None:
    response = getattr(client, method)(path)

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing Authorization header"}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/api/v1/favorites"),
        ("get", f"/api/v1/favorites/{favorite_property_ids(1)[0]}"),
        ("post", f"/api/v1/favorites/{favorite_property_ids(1)[0]}"),
        ("delete", f"/api/v1/favorites/{favorite_property_ids(1)[0]}"),
    ],
)
def test_favorites_endpoints_reject_admin_users(
    client: TestClient,
    method: str,
    path: str,
) -> None:
    response = getattr(client, method)(path, headers=auth_headers(role="admin"))

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}
