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
from app.schemas.property import PropertyStatus
from app.schemas.search import SearchFilters
from app.services.search.service import search


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
        "created_at": "2026-04-22T09:15:00+00:00",
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
        "created_at": "2026-04-21T18:05:00+00:00",
    },
    {
        "id": "prop_004",
        "title": "Hilltop Estate",
        "description": "Large estate with panoramic valley views.",
        "price": 1650000.0,
        "location": "Austin, TX",
        "bedrooms": 5,
        "bathrooms": 4,
        "area_sqm": 320.0,
        "images": [],
        "status": "available",
        "created_at": "2026-04-20T12:00:00+00:00",
    },
    {
        "id": "prop_005",
        "title": "Marina Condo",
        "description": "Waterfront condo near the marina.",
        "price": 739000.0,
        "location": "San Diego, CA",
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqm": 88.0,
        "images": [],
        "status": "available",
        "created_at": "2026-04-19T10:30:00+00:00",
    },
    {
        "id": "prop_006",
        "title": "Forest Lodge",
        "description": "Timber lodge backing onto reserve land.",
        "price": 1320000.0,
        "location": "Bend, OR",
        "bedrooms": 5,
        "bathrooms": 3,
        "area_sqm": 240.0,
        "images": [],
        "status": "available",
        "created_at": "2026-04-18T08:45:00+00:00",
    },
    {
        "id": "prop_007",
        "title": "City Loft",
        "description": "Open-plan loft close to downtown transit.",
        "price": 910000.0,
        "location": "Chicago, IL",
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqm": 102.0,
        "images": [],
        "status": "available",
        "created_at": "2026-04-17T11:20:00+00:00",
    },
    {
        "id": "prop_008",
        "title": "Vineyard House",
        "description": "Expansive residence surrounded by vines.",
        "price": 2210000.0,
        "location": "Napa, CA",
        "bedrooms": 6,
        "bathrooms": 5,
        "area_sqm": 355.0,
        "images": [],
        "status": "sold",
        "created_at": "2026-04-16T14:40:00+00:00",
    },
    {
        "id": "prop_009",
        "title": "Lake Cabin",
        "description": "Cozy cabin with private dock access.",
        "price": 680000.0,
        "location": "Madison, WI",
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqm": 120.0,
        "images": [],
        "status": "available",
        "created_at": "2026-04-15T09:00:00+00:00",
    },
    {
        "id": "prop_010",
        "title": "Garden Duplex",
        "description": "Duplex with landscaped courtyard garden.",
        "price": 870000.0,
        "location": "Portland, ME",
        "bedrooms": 4,
        "bathrooms": 3,
        "area_sqm": 145.0,
        "images": [],
        "status": "available",
        "created_at": "2026-04-14T13:10:00+00:00",
    },
    {
        "id": "prop_011",
        "title": "Riverfront Flat",
        "description": "Bright flat overlooking the riverwalk.",
        "price": 845000.0,
        "location": "Richmond, VA",
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqm": 98.0,
        "images": [],
        "status": "available",
        "created_at": "2026-04-13T07:55:00+00:00",
    },
    {
        "id": "prop_012",
        "title": "Cliffside Villa",
        "description": "Modern villa with dramatic ocean views.",
        "price": 3100000.0,
        "location": "Malibu, CA",
        "bedrooms": 4,
        "bathrooms": 4,
        "area_sqm": 280.0,
        "images": [],
        "status": "sold",
        "created_at": "2026-04-12T15:25:00+00:00",
    },
]


def _mock_supabase(properties: list[dict[str, object]]) -> MagicMock:
    client = MagicMock()

    def _table(name: str) -> MagicMock:
        table = MagicMock()
        ctx: dict[str, object] = {"filters": [], "limit": None}

        table.select.side_effect = lambda *args, **kwargs: table
        table.eq.side_effect = lambda column, value: (
            ctx["filters"].append((column, value)) or table
        )
        table.limit.side_effect = lambda value: (ctx.update({"limit": value}) or table)

        def _execute() -> MagicMock:
            response = MagicMock()
            filters = ctx["filters"]
            assert isinstance(filters, list)
            rows = [
                row
                for row in properties
                if all(row.get(column) == value for column, value in filters)
            ]
            limit = ctx["limit"]
            if isinstance(limit, int):
                rows = rows[:limit]
            response.data = copy.deepcopy(rows)
            return response

        table.execute.side_effect = _execute
        return table

    client.table.side_effect = _table
    return client


@pytest.fixture(autouse=True)
def auth_settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    get_settings.cache_clear()

    mock_client = _mock_supabase(copy.deepcopy(_TEST_PROPERTIES))
    monkeypatch.setattr("app.data.properties.get_supabase_client", lambda: mock_client)

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
    result = search(SearchFilters(bedrooms_min=5), db_session=None)

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
