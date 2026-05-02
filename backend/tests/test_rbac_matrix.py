import importlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.data.properties import PROPERTIES
from app.services.favorites.service import add_favorite, favorites_store


JWT_SECRET = "test-supabase-jwt-secret"


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
        add_favorite("user-123", PROPERTIES[0].id)


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
        path_factory=lambda: f"/api/v1/properties/{PROPERTIES[0].id}",
        expected_status_by_role={"unauthenticated": 401, "user": 200, "admin": 200},
    ),
    EndpointCase(
        name="favorites_create",
        method="post",
        path_factory=lambda: f"/api/v1/favorites/{PROPERTIES[0].id}",
        expected_status_by_role={"unauthenticated": 401, "user": 201, "admin": 403},
    ),
    EndpointCase(
        name="favorites_delete",
        method="delete",
        path_factory=lambda: f"/api/v1/favorites/{PROPERTIES[0].id}",
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
        path_factory=lambda: f"/api/v1/favorites/{PROPERTIES[0].id}",
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
        path_factory=lambda: f"/api/v1/admin/properties/{PROPERTIES[0].id}",
        expected_status_by_role={"unauthenticated": 401, "user": 403, "admin": 200},
        json_factory=_admin_update_payload,
    ),
    EndpointCase(
        name="admin_delete_property",
        method="delete",
        path_factory=lambda: f"/api/v1/admin/properties/{PROPERTIES[0].id}",
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
    monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    get_settings.cache_clear()

    original_properties = [property_item.model_copy(deep=True) for property_item in PROPERTIES]
    favorites_store.clear()
    yield
    PROPERTIES[:] = [property_item.model_copy(deep=True) for property_item in original_properties]
    favorites_store.clear()
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
