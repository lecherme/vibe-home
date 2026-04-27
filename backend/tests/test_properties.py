from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.properties.router import router as properties_router
from app.core.config import get_settings
from app.data.properties import get_all


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
    app.include_router(properties_router, prefix="/api/v1/properties")
    return TestClient(app)


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


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {build_token()}"}


def test_list_properties_returns_paginated_results(client: TestClient) -> None:
    sorted_properties = sorted(
        get_all(),
        key=lambda property_item: property_item.created_at,
        reverse=True,
    )
    expected_ids = [property_item.id for property_item in sorted_properties[5:10]]

    response = client.get(
        "/api/v1/properties",
        params={"page": 2, "page_size": 5},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == len(get_all())
    assert data["page"] == 2
    assert data["page_size"] == 5
    assert [item["id"] for item in data["items"]] == expected_ids


def test_list_properties_sorted_by_created_at_descending(client: TestClient) -> None:
    response = client.get(
        "/api/v1/properties",
        params={"page": 1, "page_size": 12},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    created_at_values = [item["created_at"] for item in response.json()["items"]]
    assert created_at_values == sorted(created_at_values, reverse=True)


def test_list_properties_clamps_page_size_to_maximum(client: TestClient) -> None:
    response = client.get(
        "/api/v1/properties",
        params={"page": 1, "page_size": 999},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["page_size"] == 50
    assert len(data["items"]) == len(get_all())


def test_list_properties_returns_empty_items_beyond_available_range(client: TestClient) -> None:
    response = client.get(
        "/api/v1/properties",
        params={"page": 999, "page_size": 12},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "total": len(get_all()),
        "page": 999,
        "page_size": 12,
    }


def test_get_property_returns_single_property(client: TestClient) -> None:
    expected_property = get_all()[0]

    response = client.get(
        f"/api/v1/properties/{expected_property.id}",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["id"] == expected_property.id
    assert response.json()["title"] == expected_property.title


def test_get_property_returns_404_for_unknown_id(client: TestClient) -> None:
    response = client.get(
        "/api/v1/properties/does-not-exist",
        headers=auth_headers(),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Property not found"}


@pytest.mark.parametrize("path", ["/api/v1/properties", "/api/v1/properties/prop_001"])
def test_property_endpoints_require_authorization(client: TestClient, path: str) -> None:
    response = client.get(path)

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing Authorization header"}
