import copy
import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.testclient import TestClient

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
_PARAM_PROPERTY_ID = _TEST_PROPERTIES[0]["id"]


def _load_favorites_test_modules() -> tuple[object, ModuleType]:
    app_root = Path(__file__).resolve().parents[1] / "app"
    service_path = app_root / "services" / "favorites" / "service.py"
    router_path = app_root / "api" / "v1" / "favorites" / "router.py"
    package_name = "app.services.favorites"
    service_name = "app.services.favorites.service"

    previous_package = sys.modules.get(package_name)
    previous_service = sys.modules.get(service_name)

    favorites_package = ModuleType(package_name)
    favorites_package.__path__ = [str(service_path.parent)]
    sys.modules[package_name] = favorites_package

    service_spec = importlib.util.spec_from_file_location(service_name, service_path)
    assert service_spec is not None and service_spec.loader is not None
    service_module = importlib.util.module_from_spec(service_spec)
    sys.modules[service_name] = service_module
    service_spec.loader.exec_module(service_module)

    favorites_package.add_favorite = service_module.add_favorite
    favorites_package.get_user_favorites = service_module.get_user_favorites
    favorites_package.remove_favorite = service_module.remove_favorite

    router_spec = importlib.util.spec_from_file_location(
        "backend_tests_favorites_router",
        router_path,
    )
    assert router_spec is not None and router_spec.loader is not None
    router_module = importlib.util.module_from_spec(router_spec)
    router_spec.loader.exec_module(router_module)

    if previous_package is None:
        sys.modules.pop(package_name, None)
    else:
        sys.modules[package_name] = previous_package

    if previous_service is None:
        sys.modules.pop(service_name, None)
    else:
        sys.modules[service_name] = previous_service

    return router_module.router, service_module


def _mock_supabase(
    properties: list[dict[str, object]],
    favorites: list[dict[str, object]],
) -> MagicMock:
    client = MagicMock()

    def _table(name: str) -> MagicMock:
        table = MagicMock()
        ctx: dict[str, object] = {"op": "select", "filters": [], "payload": None, "limit": None}
        store = properties if name == "properties" else favorites

        table.select.side_effect = lambda *a, **kw: (ctx.update({"op": "select"}) or table)
        table.insert.side_effect = lambda payload: (
            ctx.update({"op": "insert", "payload": payload}) or table
        )
        table.delete.side_effect = lambda: (ctx.update({"op": "delete"}) or table)
        table.eq.side_effect = lambda column, value: (
            ctx["filters"].append((column, value)) or table
        )
        table.limit.side_effect = lambda value: (ctx.update({"limit": value}) or table)

        def _execute() -> MagicMock:
            response = MagicMock()
            filters = ctx["filters"]
            assert isinstance(filters, list)
            matched = [row for row in store if all(row.get(column) == value for column, value in filters)]

            if ctx["op"] == "select":
                rows = copy.deepcopy(matched)
                limit = ctx["limit"]
                if isinstance(limit, int):
                    rows = rows[:limit]
                response.data = rows
            elif ctx["op"] == "insert":
                payload = ctx["payload"]
                assert isinstance(payload, dict)
                new_row = copy.deepcopy(payload)
                store.append(new_row)
                response.data = [copy.deepcopy(new_row)]
            else:
                removed_ids = {id(row) for row in matched}
                store[:] = [row for row in store if id(row) not in removed_ids]
                response.data = copy.deepcopy(matched)

            return response

        table.execute.side_effect = _execute
        return table

    client.table.side_effect = _table
    return client


FAVORITES_ROUTER, FAVORITES_SERVICE = _load_favorites_test_modules()
add_favorite = FAVORITES_SERVICE.add_favorite
get_user_favorites = FAVORITES_SERVICE.get_user_favorites
is_favorite = FAVORITES_SERVICE.is_favorite
remove_favorite = FAVORITES_SERVICE.remove_favorite


@pytest.fixture(autouse=True)
def test_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
    monkeypatch.setenv("SUPABASE_KEY", "test-service-role-key")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    get_settings.cache_clear()

    properties = copy.deepcopy(_TEST_PROPERTIES)
    favorites: list[dict[str, object]] = []
    mock_client = _mock_supabase(properties, favorites)

    monkeypatch.setattr("app.data.properties.get_supabase_client", lambda: mock_client)
    monkeypatch.setattr(FAVORITES_SERVICE, "get_supabase_client", lambda: mock_client)

    yield

    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(FAVORITES_ROUTER, prefix="/api/v1/favorites")
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
    assert get_user_favorites("user-123", page=1, page_size=10).total == 0


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
        ("get", f"/api/v1/favorites/{_PARAM_PROPERTY_ID}"),
        ("post", f"/api/v1/favorites/{_PARAM_PROPERTY_ID}"),
        ("delete", f"/api/v1/favorites/{_PARAM_PROPERTY_ID}"),
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
        ("get", f"/api/v1/favorites/{_PARAM_PROPERTY_ID}"),
        ("post", f"/api/v1/favorites/{_PARAM_PROPERTY_ID}"),
        ("delete", f"/api/v1/favorites/{_PARAM_PROPERTY_ID}"),
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
