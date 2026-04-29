from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.properties.router import router as properties_router
from app.core.config import get_settings
from app.data.properties import get_all
from app.schemas.property import PropertyStatus
from app.schemas.search import SearchFilters
from app.services.search.service import search


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


def expected_sorted_ids() -> list[str]:
    return [
        property_item.id
        for property_item in sorted(
            get_all(),
            key=lambda property_item: property_item.created_at,
            reverse=True,
        )
    ]


def test_search_service_returns_all_property_ids_for_empty_filters() -> None:
    result = search(SearchFilters(), db_session=None)

    assert result == expected_sorted_ids()


def test_search_service_filters_by_location_substring_case_insensitively() -> None:
    result = search(SearchFilters(location="BROOK"), db_session=None)

    assert result == ["prop_003"]


def test_search_service_filters_by_inclusive_price_range() -> None:
    result = search(
        SearchFilters(min_price=739000, max_price=845000),
        db_session=None,
    )

    assert result == ["prop_005", "prop_011"]


def test_search_service_filters_by_minimum_bedroom_count() -> None:
    result = search(SearchFilters(bedrooms=5), db_session=None)

    assert result == ["prop_004", "prop_006", "prop_008"]


def test_search_service_filters_by_exact_status_match() -> None:
    result = search(SearchFilters(status=PropertyStatus.SOLD.value), db_session=None)

    assert result == ["prop_003", "prop_008", "prop_012"]


def test_search_endpoint_returns_all_properties_with_default_pagination(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/properties/search", headers=auth_headers())

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == len(get_all())
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert [item["id"] for item in data["items"]] == expected_sorted_ids()


def test_search_endpoint_rejects_negative_price_filters(client: TestClient) -> None:
    response = client.get(
        "/api/v1/properties/search",
        params={"min_price": -1},
        headers=auth_headers(),
    )

    assert response.status_code == 422


def test_search_endpoint_rejects_invalid_status_filters(client: TestClient) -> None:
    response = client.get(
        "/api/v1/properties/search",
        params={"status": "pending"},
        headers=auth_headers(),
    )

    assert response.status_code == 422


def test_search_endpoint_caps_page_size_at_100(client: TestClient) -> None:
    response = client.get(
        "/api/v1/properties/search",
        params={"page_size": 999},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()

    assert data["page_size"] == 100
    assert len(data["items"]) == len(get_all())
