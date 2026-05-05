import copy
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.properties.router import router as properties_router
from app.core.config import get_settings
from app.data.properties import get_all


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
    {
        "id": "prop_003",
        "title": "Parkside Brownstone",
        "description": "Renovated brownstone with original millwork.",
        "price": 1985000.0,
        "location": "Brooklyn, NY",
        "bedrooms": 4,
        "bathrooms": 3,
        "area_sqm": 196.8,
        "images": [],
        "status": "sold",
        "created_at": "2026-04-19T18:05:00+00:00",
    },
]


def _mock_supabase(properties: list, favorites: list) -> MagicMock:
    client = MagicMock()

    def _table(name: str) -> MagicMock:
        t = MagicMock()
        ctx: dict = {"op": "select", "filters": [], "payload": None, "limit": None}
        store = properties if name == "properties" else favorites

        t.select.side_effect = lambda *a, **kw: (ctx.update({"op": "select"}) or t)
        t.insert.side_effect = lambda d: (ctx.update({"op": "insert", "payload": d}) or t)
        t.update.side_effect = lambda d: (ctx.update({"op": "update", "payload": d}) or t)
        t.delete.side_effect = lambda: (ctx.update({"op": "delete"}) or t)
        t.eq.side_effect = lambda c, v: (ctx["filters"].append((c, v)) or t)
        t.limit.side_effect = lambda n: (ctx.update({"limit": n}) or t)

        def _execute() -> MagicMock:
            resp = MagicMock()
            filt = ctx["filters"]
            matched = [r for r in store if all(r.get(c) == v for c, v in filt)]
            if ctx["op"] == "select":
                rows = copy.deepcopy(matched)
                if ctx["limit"] is not None:
                    rows = rows[: ctx["limit"]]
                resp.data = rows
            elif ctx["op"] == "insert":
                new_row = copy.deepcopy(ctx["payload"])
                store.append(new_row)
                resp.data = [copy.deepcopy(new_row)]
            elif ctx["op"] == "update":
                for row in store:
                    if all(row.get(c) == v for c, v in filt):
                        row.update(ctx["payload"])
                resp.data = [copy.deepcopy(r) for r in store if all(r.get(c) == v for c, v in filt)]
            elif ctx["op"] == "delete":
                removed_ids = {id(r) for r in matched}
                keep = [r for r in store if id(r) not in removed_ids]
                if name == "properties":
                    properties[:] = keep
                    gone = {r["id"] for r in matched}
                    favorites[:] = [f for f in favorites if f.get("property_id") not in gone]
                else:
                    favorites[:] = keep
                resp.data = copy.deepcopy(matched)
            return resp

        t.execute.side_effect = _execute
        return t

    client.table.side_effect = _table
    return client


@pytest.fixture(autouse=True)
def auth_settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    get_settings.cache_clear()

    properties = copy.deepcopy(_TEST_PROPERTIES)
    favorites: list = []
    mock_client = _mock_supabase(properties, favorites)

    monkeypatch.setattr("app.data.properties.get_supabase_client", lambda: mock_client)
    monkeypatch.setattr("app.services.admin.service.get_supabase_client", lambda: mock_client)

    yield


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
