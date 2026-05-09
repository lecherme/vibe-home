import copy
from datetime import datetime, timedelta, timezone
from typing import Optional
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.v1.admin.router import router as admin_router
from app.api.v1.properties.router import router as properties_router
from app.core.config import get_settings
from app.schemas.admin import PropertyCreate, PropertyUpdate
from app.services.admin.service import create_property, delete_property, update_property


JWT_SECRET = "test-supabase-jwt-secret"

_TEST_PROPERTIES = [
    {
        "id": "prop_001",
        "title": "Harbor View Penthouse",
        "description": "Top-floor penthouse with wraparound windows.",
        "price": 2450000.0,
        "location": "Seattle, WA",
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqm": 182.5,
        "images": [],
        "status": "available",
        "created_at": "2026-04-23T16:30:00+00:00",
    },
    {
        "id": "prop_002",
        "title": "Desert Courtyard Retreat",
        "description": "Single-level home with a shaded courtyard.",
        "price": 1180000.0,
        "location": "Scottsdale, AZ",
        "bedrooms": 4,
        "bathrooms": 3,
        "area_sqm": 210.2,
        "images": [],
        "status": "available",
        "created_at": "2026-04-21T09:15:00+00:00",
    },
]

_TEST_FAVORITES = [
    {
        "user_id": "user-123",
        "property_id": "prop_001",
        "created_at": "2026-04-24T12:00:00+00:00",
    },
    {
        "user_id": "user-456",
        "property_id": "prop_001",
        "created_at": "2026-04-24T12:05:00+00:00",
    },
    {
        "user_id": "user-123",
        "property_id": "prop_002",
        "created_at": "2026-04-24T12:10:00+00:00",
    },
]


def _mock_supabase(
    properties: list[dict[str, object]],
    favorites: list[dict[str, object]],
) -> MagicMock:
    client = MagicMock()

    def _table(name: str) -> MagicMock:
        if name not in {"properties", "favorites"}:
            raise AssertionError(f"Unexpected table requested: {name}")

        table = MagicMock()
        context: dict[str, object] = {
            "op": "select",
            "filters": [],
            "payload": None,
            "limit": None,
        }
        store = properties if name == "properties" else favorites

        table.select.side_effect = lambda *args, **kwargs: (context.update({"op": "select"}) or table)
        table.insert.side_effect = lambda payload: (context.update({"op": "insert", "payload": payload}) or table)
        table.update.side_effect = lambda payload: (context.update({"op": "update", "payload": payload}) or table)
        table.delete.side_effect = lambda: (context.update({"op": "delete"}) or table)
        table.eq.side_effect = (
            lambda column, value: (context["filters"].append((column, value)) or table)
        )
        table.limit.side_effect = lambda value: (context.update({"limit": value}) or table)

        def _execute() -> MagicMock:
            response = MagicMock()
            filters = context["filters"]
            matched = [row for row in store if all(row.get(column) == value for column, value in filters)]

            if context["op"] == "select":
                rows = copy.deepcopy(matched)
                if context["limit"] is not None:
                    rows = rows[: context["limit"]]
                response.data = rows
            elif context["op"] == "insert":
                new_row = copy.deepcopy(context["payload"])
                store.append(new_row)
                response.data = [copy.deepcopy(new_row)]
            elif context["op"] == "update":
                for row in store:
                    if all(row.get(column) == value for column, value in filters):
                        row.update(context["payload"])
                response.data = [
                    copy.deepcopy(row)
                    for row in store
                    if all(row.get(column) == value for column, value in filters)
                ]
            elif context["op"] == "delete":
                removed_ids = {id(row) for row in matched}
                store[:] = [row for row in store if id(row) not in removed_ids]
                response.data = copy.deepcopy(matched)
            else:
                raise AssertionError(f"Unexpected operation: {context['op']}")

            return response

        table.execute.side_effect = _execute
        return table

    client.table.side_effect = _table
    return client


@pytest.fixture(autouse=True)
def test_state(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[dict[str, object]]]:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-service-role-key")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    get_settings.cache_clear()

    properties = copy.deepcopy(_TEST_PROPERTIES)
    favorites = copy.deepcopy(_TEST_FAVORITES)
    mock_client = _mock_supabase(properties, favorites)
    monkeypatch.setattr("app.data.properties.get_supabase_client", lambda: mock_client)
    monkeypatch.setattr("app.services.admin.service.get_supabase_client", lambda: mock_client)

    yield {"properties": properties, "favorites": favorites}

    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(admin_router, prefix="/api/v1/admin")
    app.include_router(properties_router, prefix="/api/v1/properties")
    return TestClient(app)


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


def test_create_property_service_adds_property_to_shared_store(
    test_state: dict[str, list[dict[str, object]]],
) -> None:
    property_item = create_property(PropertyCreate(**property_payload()))

    assert property_item.id.startswith("prop_")
    assert property_item.status == "available"
    assert property_item.area_sqm == 142.8
    assert property_item.images == ["https://example.com/property.jpg"]
    assert any(saved_property["id"] == property_item.id for saved_property in test_state["properties"])


def test_update_property_service_applies_partial_updates(
    test_state: dict[str, list[dict[str, object]]],
) -> None:
    original_property = test_state["properties"][0]

    updated_property = update_property(
        str(original_property["id"]),
        PropertyUpdate(price=1110000.0, area=199.5, image_url=""),
    )

    assert updated_property.id == original_property["id"]
    assert updated_property.price == 1110000.0
    assert updated_property.area_sqm == 199.5
    assert updated_property.images == []
    assert test_state["properties"][0]["price"] == 1110000.0


def test_delete_property_service_removes_property_from_shared_store(
    test_state: dict[str, list[dict[str, object]]],
) -> None:
    property_id = str(test_state["properties"][0]["id"])

    delete_property(property_id)

    assert all(property_item["id"] != property_id for property_item in test_state["properties"])
    assert all(favorite["property_id"] != property_id for favorite in test_state["favorites"])


def test_post_admin_property_creates_property_and_returns_201(
    client: TestClient,
    test_state: dict[str, list[dict[str, object]]],
) -> None:
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
    assert any(property_item["id"] == data["id"] for property_item in test_state["properties"])


def test_post_admin_property_returns_422_for_missing_required_fields(client: TestClient) -> None:
    response = client.post(
        "/api/v1/admin/properties",
        headers=auth_headers(),
        json={"title": "Incomplete Property"},
    )

    assert response.status_code == 422


def test_put_admin_property_updates_property_and_returns_200(
    client: TestClient,
    test_state: dict[str, list[dict[str, object]]],
) -> None:
    property_id = str(test_state["properties"][0]["id"])

    response = client.put(
        f"/api/v1/admin/properties/{property_id}",
        headers=auth_headers(),
        json={"price": 1234567.0, "location": "San Diego, CA"},
    )

    assert response.status_code == 200
    assert response.json()["price"] == 1234567.0
    assert response.json()["location"] == "San Diego, CA"
    assert test_state["properties"][0]["price"] == 1234567.0


def test_put_admin_property_returns_404_for_missing_property(client: TestClient) -> None:
    response = client.put(
        "/api/v1/admin/properties/does-not-exist",
        headers=auth_headers(),
        json={"price": 1234567.0},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Property not found"}


def test_delete_admin_property_removes_property_and_returns_204(
    client: TestClient,
    test_state: dict[str, list[dict[str, object]]],
) -> None:
    property_id = str(test_state["properties"][0]["id"])

    response = client.delete(
        f"/api/v1/admin/properties/{property_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 204
    assert response.content == b""
    assert all(property_item["id"] != property_id for property_item in test_state["properties"])
    assert all(favorite["property_id"] != property_id for favorite in test_state["favorites"])


def test_delete_admin_property_returns_404_for_missing_property(client: TestClient) -> None:
    response = client.delete(
        "/api/v1/admin/properties/does-not-exist",
        headers=auth_headers(),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Property not found"}


def test_deleted_property_is_absent_from_public_properties_list(
    client: TestClient,
    test_state: dict[str, list[dict[str, object]]],
) -> None:
    property_id = str(test_state["properties"][0]["id"])

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
    ("method", "path_template", "payload"),
    [
        ("post", "/api/v1/admin/properties", property_payload()),
        ("put", "/api/v1/admin/properties/{property_id}", {"price": 999999.0}),
        ("delete", "/api/v1/admin/properties/{property_id}", None),
    ],
)
def test_admin_endpoints_require_authentication(
    client: TestClient,
    test_state: dict[str, list[dict[str, object]]],
    method: str,
    path_template: str,
    payload: Optional[dict[str, object]],
) -> None:
    path = path_template.format(property_id=test_state["properties"][0]["id"])
    response = request(client, method, path, json=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing Authorization header"}


@pytest.mark.parametrize(
    ("method", "path_template", "payload"),
    [
        ("post", "/api/v1/admin/properties", property_payload()),
        ("put", "/api/v1/admin/properties/{property_id}", {"price": 999999.0}),
        ("delete", "/api/v1/admin/properties/{property_id}", None),
    ],
)
def test_admin_endpoints_reject_non_admin_users(
    client: TestClient,
    test_state: dict[str, list[dict[str, object]]],
    method: str,
    path_template: str,
    payload: Optional[dict[str, object]],
) -> None:
    path = path_template.format(property_id=test_state["properties"][0]["id"])
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
