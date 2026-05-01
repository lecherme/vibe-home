import importlib
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.data.properties import PROPERTIES
from app.schemas.admin import PropertyCreate, PropertyUpdate
from app.services.admin.service import create_property, delete_property, update_property


JWT_SECRET = "test-supabase-jwt-secret"


@pytest.fixture(autouse=True)
def test_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    get_settings.cache_clear()

    original_properties = [property_item.model_copy(deep=True) for property_item in PROPERTIES]
    yield
    PROPERTIES[:] = [property_item.model_copy(deep=True) for property_item in original_properties]
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    import app.main as main_module

    main_module = importlib.reload(main_module)
    return TestClient(main_module.app)


def build_token(
    *,
    role: str = "admin",
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


def auth_headers(*, role: str = "admin") -> dict[str, str]:
    return {"Authorization": f"Bearer {build_token(role=role)}"}


def property_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "title": "Oceanfront Bungalow",
        "description": "Single-story home with a wraparound deck.",
        "price": 980000.0,
        "location": "Santa Cruz, CA",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": 142.8,
        "image_url": "https://example.com/property.jpg",
    }
    payload.update(overrides)
    return payload


def request(
    client: TestClient,
    method: str,
    path: str,
    *,
    headers: Optional[dict[str, str]] = None,
    json: Optional[dict[str, object]] = None,
):
    kwargs = {"headers": headers}
    if json is not None:
        kwargs["json"] = json

    return getattr(client, method)(path, **kwargs)


def test_create_property_service_adds_property_to_shared_store() -> None:
    property_item = create_property(PropertyCreate(**property_payload()))

    assert property_item.id.startswith("prop_")
    assert property_item.status == "available"
    assert property_item.area_sqm == 142.8
    assert property_item.images == ["https://example.com/property.jpg"]
    assert any(saved_property.id == property_item.id for saved_property in PROPERTIES)


def test_update_property_service_applies_partial_updates() -> None:
    original_property = PROPERTIES[0]

    updated_property = update_property(
        original_property.id,
        PropertyUpdate(price=1110000.0, area=199.5, image_url=""),
    )

    assert updated_property.id == original_property.id
    assert updated_property.price == 1110000.0
    assert updated_property.area_sqm == 199.5
    assert updated_property.images == []
    assert PROPERTIES[0].price == 1110000.0


def test_delete_property_service_removes_property_from_shared_store() -> None:
    property_id = PROPERTIES[0].id

    delete_property(property_id)

    assert all(property_item.id != property_id for property_item in PROPERTIES)


def test_post_admin_property_creates_property_and_returns_201(client: TestClient) -> None:
    response = client.post(
        "/api/v1/admin/properties",
        headers=auth_headers(),
        json=property_payload(),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"].startswith("prop_")
    assert data["title"] == "Oceanfront Bungalow"
    assert data["status"] == "available"
    assert data["area_sqm"] == 142.8
    assert data["images"] == ["https://example.com/property.jpg"]
    assert data["created_at"]
    assert any(property_item.id == data["id"] for property_item in PROPERTIES)


def test_post_admin_property_returns_422_for_missing_required_fields(client: TestClient) -> None:
    response = client.post(
        "/api/v1/admin/properties",
        headers=auth_headers(),
        json={"title": "Incomplete Property"},
    )

    assert response.status_code == 422


def test_put_admin_property_updates_property_and_returns_200(client: TestClient) -> None:
    property_id = PROPERTIES[0].id

    response = client.put(
        f"/api/v1/admin/properties/{property_id}",
        headers=auth_headers(),
        json={"price": 1234567.0, "location": "San Diego, CA"},
    )

    assert response.status_code == 200
    assert response.json()["price"] == 1234567.0
    assert response.json()["location"] == "San Diego, CA"
    assert PROPERTIES[0].price == 1234567.0


def test_put_admin_property_returns_404_for_missing_property(client: TestClient) -> None:
    response = client.put(
        "/api/v1/admin/properties/does-not-exist",
        headers=auth_headers(),
        json={"price": 1234567.0},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Property not found"}


def test_delete_admin_property_removes_property_and_returns_204(client: TestClient) -> None:
    property_id = PROPERTIES[0].id

    response = client.delete(
        f"/api/v1/admin/properties/{property_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 204
    assert response.content == b""
    assert all(property_item.id != property_id for property_item in PROPERTIES)


def test_delete_admin_property_returns_404_for_missing_property(client: TestClient) -> None:
    response = client.delete(
        "/api/v1/admin/properties/does-not-exist",
        headers=auth_headers(),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Property not found"}


def test_deleted_property_is_absent_from_public_properties_list(client: TestClient) -> None:
    property_id = PROPERTIES[0].id

    delete_response = client.delete(
        f"/api/v1/admin/properties/{property_id}",
        headers=auth_headers(),
    )
    list_response = client.get(
        "/api/v1/properties",
        headers=auth_headers(role="user"),
    )

    assert delete_response.status_code == 204
    assert list_response.status_code == 200
    assert property_id not in [item["id"] for item in list_response.json()["items"]]


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("post", "/api/v1/admin/properties", property_payload()),
        ("put", f"/api/v1/admin/properties/{PROPERTIES[0].id}", {"price": 999999.0}),
        ("delete", f"/api/v1/admin/properties/{PROPERTIES[0].id}", None),
    ],
)
def test_admin_endpoints_require_authentication(
    client: TestClient,
    method: str,
    path: str,
    payload: Optional[dict[str, object]],
) -> None:
    response = request(client, method, path, json=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing Authorization header"}


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("post", "/api/v1/admin/properties", property_payload()),
        ("put", f"/api/v1/admin/properties/{PROPERTIES[0].id}", {"price": 999999.0}),
        ("delete", f"/api/v1/admin/properties/{PROPERTIES[0].id}", None),
    ],
)
def test_admin_endpoints_reject_non_admin_users(
    client: TestClient,
    method: str,
    path: str,
    payload: Optional[dict[str, object]],
) -> None:
    response = request(client, method, path, headers=auth_headers(role="user"), json=payload)

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}


def test_update_property_service_raises_404_for_missing_property() -> None:
    with pytest.raises(HTTPException) as exc_info:
        update_property("does-not-exist", PropertyUpdate(title="Updated"))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Property not found"


def test_delete_property_service_raises_404_for_missing_property() -> None:
    with pytest.raises(HTTPException) as exc_info:
        delete_property("does-not-exist")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Property not found"
