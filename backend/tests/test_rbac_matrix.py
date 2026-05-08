import copy
import importlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.services.favorites.service import add_favorite


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
_PARAM_PROPERTY_ID = _TEST_PROPERTIES[0]["id"]


def _mock_supabase(
    properties: list[dict[str, object]],
    favorites: list[dict[str, object]],
) -> MagicMock:
    client = MagicMock()

    def _table(name: str) -> MagicMock:
        table = MagicMock()
        context: dict[str, object] = {
            "op": "select",
            "filters": [],
            "payload": None,
            "limit": None,
        }
        store = properties if name == "properties" else favorites

        table.select.side_effect = lambda *args, **kwargs: (context.update({"op": "select"}) or table)
        table.insert.side_effect = lambda payload: (
            context.update({"op": "insert", "payload": payload}) or table
        )
        table.update.side_effect = lambda payload: (
            context.update({"op": "update", "payload": payload}) or table
        )
        table.delete.side_effect = lambda: (context.update({"op": "delete"}) or table)
        table.eq.side_effect = (
            lambda column, value: (context["filters"].append((column, value)) or table)
        )
        table.limit.side_effect = lambda value: (context.update({"limit": value}) or table)

        def _execute() -> MagicMock:
            response = MagicMock()
            filters = context["filters"]
            assert isinstance(filters, list)
            matched = [
                row for row in store if all(row.get(column) == value for column, value in filters)
            ]

            if context["op"] == "select":
                rows = copy.deepcopy(matched)
                limit = context["limit"]
                if isinstance(limit, int):
                    rows = rows[:limit]
                response.data = rows
            elif context["op"] == "insert":
                payload = context["payload"]
                assert isinstance(payload, dict)
                new_row = copy.deepcopy(payload)
                store.append(new_row)
                response.data = [copy.deepcopy(new_row)]
            elif context["op"] == "update":
                payload = context["payload"]
                assert isinstance(payload, dict)
                for row in store:
                    if all(row.get(column) == value for column, value in filters):
                        row.update(payload)
                response.data = [
                    copy.deepcopy(row)
                    for row in store
                    if all(row.get(column) == value for column, value in filters)
                ]
            else:
                removed_ids = {id(row) for row in matched}
                keep = [row for row in store if id(row) not in removed_ids]
                if name == "properties":
                    properties[:] = keep
                    removed_property_ids = {row["id"] for row in matched}
                    favorites[:] = [
                        favorite
                        for favorite in favorites
                        if favorite.get("property_id") not in removed_property_ids
                    ]
                else:
                    favorites[:] = keep
                response.data = copy.deepcopy(matched)

            return response

        table.execute.side_effect = _execute
        return table

    client.table.side_effect = _table
    return client


@dataclass(frozen=True)
class EndpointCase:
    name: str
    method: str
    path_factory: Callable[[], str]
    expected_status_by_role: dict[str, int]
    json_factory: Optional[Callable[[], Optional[dict[str, Any]]]] = None
    setup_by_role: Optional[Callable[[str], None]] = None


def _admin_create_payload() -> dict[str, object]:
    return {
        "title": "RBAC Test Property",
        "description": "Property payload for access control verification.",
        "price": 980000.0,
        "location": "Santa Cruz, CA",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": 142.8,
        "image_url": "https://example.com/property.jpg",
    }


def _admin_update_payload() -> dict[str, object]:
    return {
        "price": 1234567.0,
        "location": "San Diego, CA",
    }


def _favorite_setup(role: str) -> None:
    if role == "user":
        add_favorite("user-123", _PARAM_PROPERTY_ID)


RBAC_CASES = [
    EndpointCase(
        name="auth_me",
        method="get",
        path_factory=lambda: "/api/v1/auth/me",
        expected_status_by_role={"unauthenticated": 401, "user": 200, "admin": 200},
    ),
    EndpointCase(
        name="properties_list",
        method="get",
        path_factory=lambda: "/api/v1/properties",
        expected_status_by_role={"unauthenticated": 401, "user": 200, "admin": 200},
    ),
    EndpointCase(
        name="properties_search",
        method="get",
        path_factory=lambda: "/api/v1/properties/search",
        expected_status_by_role={"unauthenticated": 401, "user": 200, "admin": 200},
    ),
    EndpointCase(
        name="properties_detail",
        method="get",
        path_factory=lambda: f"/api/v1/properties/{_PARAM_PROPERTY_ID}",
        expected_status_by_role={"unauthenticated": 401, "user": 200, "admin": 200},
    ),
    EndpointCase(
        name="favorites_create",
        method="post",
        path_factory=lambda: f"/api/v1/favorites/{_PARAM_PROPERTY_ID}",
        expected_status_by_role={"unauthenticated": 401, "user": 201, "admin": 403},
    ),
    EndpointCase(
        name="favorites_delete",
        method="delete",
        path_factory=lambda: f"/api/v1/favorites/{_PARAM_PROPERTY_ID}",
        expected_status_by_role={"unauthenticated": 401, "user": 204, "admin": 403},
        setup_by_role=_favorite_setup,
    ),
    EndpointCase(
        name="favorites_list",
        method="get",
        path_factory=lambda: "/api/v1/favorites",
        expected_status_by_role={"unauthenticated": 401, "user": 200, "admin": 403},
    ),
    EndpointCase(
        name="favorites_status",
        method="get",
        path_factory=lambda: f"/api/v1/favorites/{_PARAM_PROPERTY_ID}",
        expected_status_by_role={"unauthenticated": 401, "user": 200, "admin": 403},
    ),
    EndpointCase(
        name="admin_create_property",
        method="post",
        path_factory=lambda: "/api/v1/admin/properties",
        expected_status_by_role={"unauthenticated": 401, "user": 403, "admin": 201},
        json_factory=_admin_create_payload,
    ),
    EndpointCase(
        name="admin_update_property",
        method="put",
        path_factory=lambda: f"/api/v1/admin/properties/{_PARAM_PROPERTY_ID}",
        expected_status_by_role={"unauthenticated": 401, "user": 403, "admin": 200},
        json_factory=_admin_update_payload,
    ),
    EndpointCase(
        name="admin_delete_property",
        method="delete",
        path_factory=lambda: f"/api/v1/admin/properties/{_PARAM_PROPERTY_ID}",
        expected_status_by_role={"unauthenticated": 401, "user": 403, "admin": 204},
    ),
]


RBAC_MATRIX_PARAMS = [
    pytest.param(case, role, case.expected_status_by_role[role], id=f"{case.name}-{role}")
    for case in RBAC_CASES
    for role in ("unauthenticated", "user", "admin")
]


@pytest.fixture(autouse=True)
def test_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
    monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    get_settings.cache_clear()

    properties = copy.deepcopy(_TEST_PROPERTIES)
    favorites: list[dict[str, object]] = []
    mock_client = _mock_supabase(properties, favorites)

    monkeypatch.setattr("app.data.properties.get_supabase_client", lambda: mock_client)
    monkeypatch.setattr("app.services.admin.service.get_supabase_client", lambda: mock_client)
    monkeypatch.setattr("app.services.favorites.service.get_supabase_client", lambda: mock_client)

    yield

    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    import app.main as main_module

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


def auth_headers(role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {build_token(role=role)}"}


def request_endpoint(client: TestClient, case: EndpointCase, role: str):
    headers = None if role == "unauthenticated" else auth_headers(role)
    json_payload = case.json_factory() if case.json_factory is not None else None
    request_kwargs: dict[str, Any] = {"headers": headers}
    if json_payload is not None:
        request_kwargs["json"] = json_payload
    return getattr(client, case.method)(case.path_factory(), **request_kwargs)


@pytest.mark.parametrize(("case", "role", "expected_status"), RBAC_MATRIX_PARAMS)
def test_rbac_permission_matrix(
    client: TestClient,
    case: EndpointCase,
    role: str,
    expected_status: int,
) -> None:
    if case.setup_by_role is not None:
        case.setup_by_role(role)

    response = request_endpoint(client, case, role)

    assert response.status_code == expected_status
