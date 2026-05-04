import copy
import os
from collections.abc import Iterable
from typing import Any, Optional, Union

try:
    from supabase import Client as SupabaseClient
    from supabase import create_client
except ImportError:  # pragma: no cover - exercised indirectly in tests
    SupabaseClient = Any  # type: ignore[misc,assignment]
    create_client = None


_PROPERTY_PLACEHOLDER_IMAGES = [
    "/images/properties/property-placeholder-exterior.svg",
    "/images/properties/property-placeholder-interior.svg",
]


def _default_property(
    *,
    property_id: str,
    title: str,
    description: str,
    price: float,
    location: str,
    bedrooms: int,
    bathrooms: int,
    area_sqm: float,
    status: str,
    created_at: str,
) -> dict[str, Any]:
    return {
        "id": property_id,
        "title": title,
        "description": description,
        "price": price,
        "location": location,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "area_sqm": area_sqm,
        "images": list(_PROPERTY_PLACEHOLDER_IMAGES),
        "status": status,
        "created_at": created_at,
    }


def _default_state() -> dict[str, list[dict[str, Any]]]:
    return {
        "properties": [
            _default_property(
                property_id="prop_001",
                title="Harbor View Penthouse",
                description=(
                    "Top-floor penthouse with wraparound windows, a private terrace, and "
                    "direct elevator access overlooking the marina."
                ),
                price=2450000.0,
                location="Seattle, WA",
                bedrooms=3,
                bathrooms=2,
                area_sqm=182.5,
                status="available",
                created_at="2026-04-23T16:30:00+00:00",
            ),
            _default_property(
                property_id="prop_002",
                title="Desert Courtyard Retreat",
                description=(
                    "Single-level home with a shaded courtyard, polished concrete floors, "
                    "and a seamless indoor-outdoor entertaining layout."
                ),
                price=1180000.0,
                location="Scottsdale, AZ",
                bedrooms=4,
                bathrooms=3,
                area_sqm=210.2,
                status="available",
                created_at="2026-04-21T09:15:00+00:00",
            ),
            _default_property(
                property_id="prop_003",
                title="Parkside Brownstone",
                description=(
                    "Renovated brownstone with original millwork, chef's kitchen, and a "
                    "garden-level lounge opening onto a landscaped patio."
                ),
                price=1985000.0,
                location="Brooklyn, NY",
                bedrooms=4,
                bathrooms=3,
                area_sqm=196.8,
                status="sold",
                created_at="2026-04-19T18:05:00+00:00",
            ),
            _default_property(
                property_id="prop_004",
                title="Lakefront Glass House",
                description=(
                    "Contemporary lakefront residence with double-height living room, "
                    "sauna, and a cantilevered deck above the waterline."
                ),
                price=3125000.0,
                location="Madison, WI",
                bedrooms=5,
                bathrooms=4,
                area_sqm=328.4,
                status="available",
                created_at="2026-04-18T12:45:00+00:00",
            ),
            _default_property(
                property_id="prop_005",
                title="Historic Loft at Market Square",
                description=(
                    "Warehouse loft conversion with exposed brick, timber beams, and "
                    "oversized factory windows in a walkable downtown district."
                ),
                price=845000.0,
                location="Nashville, TN",
                bedrooms=2,
                bathrooms=2,
                area_sqm=134.1,
                status="rented",
                created_at="2026-04-17T14:20:00+00:00",
            ),
            _default_property(
                property_id="prop_006",
                title="Cliffside Villa",
                description=(
                    "Ocean-facing villa with infinity pool, detached guest suite, and "
                    "sunset terraces carved into the hillside."
                ),
                price=4290000.0,
                location="Malibu, CA",
                bedrooms=5,
                bathrooms=5,
                area_sqm=410.7,
                status="available",
                created_at="2026-04-15T08:10:00+00:00",
            ),
            _default_property(
                property_id="prop_007",
                title="River District Townhome",
                description=(
                    "Three-story townhome with rooftop lounge, attached garage, and open "
                    "kitchen-dining level near the arts district."
                ),
                price=965000.0,
                location="Portland, OR",
                bedrooms=3,
                bathrooms=3,
                area_sqm=158.0,
                status="available",
                created_at="2026-04-14T11:55:00+00:00",
            ),
            _default_property(
                property_id="prop_008",
                title="Countryside Manor",
                description=(
                    "Expansive manor home with library, conservatory, and equestrian-ready "
                    "grounds bordered by mature oak trees."
                ),
                price=2750000.0,
                location="Lexington, KY",
                bedrooms=6,
                bathrooms=5,
                area_sqm=455.6,
                status="sold",
                created_at="2026-04-12T10:00:00+00:00",
            ),
            _default_property(
                property_id="prop_009",
                title="Midtown Skyline Condo",
                description=(
                    "Corner condo with panoramic skyline views, concierge access, and a "
                    "residents-only fitness studio and lounge."
                ),
                price=1125000.0,
                location="Atlanta, GA",
                bedrooms=2,
                bathrooms=2,
                area_sqm=121.4,
                status="available",
                created_at="2026-04-11T19:40:00+00:00",
            ),
            _default_property(
                property_id="prop_010",
                title="Snowline Chalet",
                description=(
                    "Mountain chalet with vaulted timber ceilings, stone fireplace, and "
                    "heated gear room minutes from the lifts."
                ),
                price=1540000.0,
                location="Aspen, CO",
                bedrooms=4,
                bathrooms=3,
                area_sqm=187.9,
                status="rented",
                created_at="2026-04-09T07:25:00+00:00",
            ),
            _default_property(
                property_id="prop_011",
                title="Palm Grove Bungalow",
                description=(
                    "Renovated bungalow with breezy lanai, terrazzo floors, and lush "
                    "tropical planting around a saltwater plunge pool."
                ),
                price=739000.0,
                location="St. Petersburg, FL",
                bedrooms=3,
                bathrooms=2,
                area_sqm=116.3,
                status="available",
                created_at="2026-04-07T13:05:00+00:00",
            ),
            _default_property(
                property_id="prop_012",
                title="University District Duplex",
                description=(
                    "Income-friendly duplex with refreshed interiors, separate entrances, "
                    "and quick access to campus and transit."
                ),
                price=689000.0,
                location="Ann Arbor, MI",
                bedrooms=4,
                bathrooms=2,
                area_sqm=149.7,
                status="sold",
                created_at="2026-04-05T15:30:00+00:00",
            ),
            _default_property(
                property_id="prop_013",
                title="Canal House Residence",
                description=(
                    "Light-filled residence with indoor atrium, floating stair, and a "
                    "dockside deck designed for paddleboard access."
                ),
                price=1330000.0,
                location="Fort Lauderdale, FL",
                bedrooms=3,
                bathrooms=3,
                area_sqm=172.6,
                status="available",
                created_at="2026-04-03T17:50:00+00:00",
            ),
            _default_property(
                property_id="prop_014",
                title="Old Town Courtyard Flat",
                description=(
                    "Quiet courtyard flat with limestone finishes, bespoke storage, and "
                    "walkable access to cafes, galleries, and the river trail."
                ),
                price=598000.0,
                location="Savannah, GA",
                bedrooms=1,
                bathrooms=1,
                area_sqm=78.2,
                status="rented",
                created_at="2026-04-02T09:45:00+00:00",
            ),
            _default_property(
                property_id="prop_015",
                title="Forest Edge Cabin",
                description=(
                    "Minimalist timber cabin with wood stove, reading loft, and floor-to-"
                    "ceiling glazing facing a protected forest preserve."
                ),
                price=525000.0,
                location="Bend, OR",
                bedrooms=2,
                bathrooms=1,
                area_sqm=89.5,
                status="available",
                created_at="2026-03-31T20:15:00+00:00",
            ),
            _default_property(
                property_id="prop_016",
                title="Capitol Hill Row House",
                description=(
                    "Updated row house with solar panels, a lower-level studio suite, and "
                    "a brick patio designed for year-round outdoor dining."
                ),
                price=1495000.0,
                location="Washington, DC",
                bedrooms=4,
                bathrooms=3,
                area_sqm=201.0,
                status="available",
                created_at="2026-03-29T12:00:00+00:00",
            ),
        ],
        "favorites": [],
    }


class FakeSupabaseResponse:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.data = data


class FakeSupabaseTable:
    def __init__(self, state: dict[str, list[dict[str, Any]]], table_name: str) -> None:
        self._state = state
        self._table_name = table_name
        self._operation = "select"
        self._payload: Any = None
        self._filters: list[tuple[str, Any]] = []
        self._order_by: Optional[tuple[str, bool]] = None
        self._range: Optional[tuple[int, int]] = None
        self._limit: Optional[int] = None

    def select(self, columns: str = "*") -> "FakeSupabaseTable":
        del columns
        self._operation = "select"
        return self

    def insert(
        self,
        payload: Union[dict[str, Any], list[dict[str, Any]]],
    ) -> "FakeSupabaseTable":
        self._operation = "insert"
        self._payload = payload
        return self

    def update(self, payload: dict[str, Any]) -> "FakeSupabaseTable":
        self._operation = "update"
        self._payload = payload
        return self

    def delete(self) -> "FakeSupabaseTable":
        self._operation = "delete"
        return self

    def eq(self, column: str, value: Any) -> "FakeSupabaseTable":
        self._filters.append((column, value))
        return self

    def order(self, column: str, desc: bool = False) -> "FakeSupabaseTable":
        self._order_by = (column, desc)
        return self

    def range(self, start: int, end: int) -> "FakeSupabaseTable":
        self._range = (start, end)
        return self

    def limit(self, count: int) -> "FakeSupabaseTable":
        self._limit = count
        return self

    def execute(self) -> FakeSupabaseResponse:
        if self._operation == "select":
            return FakeSupabaseResponse(self._select_rows())
        if self._operation == "insert":
            return FakeSupabaseResponse(self._insert_rows())
        if self._operation == "update":
            return FakeSupabaseResponse(self._update_rows())
        if self._operation == "delete":
            return FakeSupabaseResponse(self._delete_rows())

        raise RuntimeError(f"Unsupported fake Supabase operation: {self._operation}")

    def _matching_rows(self) -> list[dict[str, Any]]:
        return [
            row
            for row in self._state[self._table_name]
            if all(row.get(column) == value for column, value in self._filters)
        ]

    def _select_rows(self) -> list[dict[str, Any]]:
        rows = [copy.deepcopy(row) for row in self._matching_rows()]
        if self._order_by is not None:
            column, desc = self._order_by
            rows.sort(key=lambda row: row.get(column), reverse=desc)
        if self._range is not None:
            start, end = self._range
            rows = rows[start : end + 1]
        if self._limit is not None:
            rows = rows[: self._limit]
        return rows

    def _insert_rows(self) -> list[dict[str, Any]]:
        rows = self._payload if isinstance(self._payload, list) else [self._payload]
        inserted_rows: list[dict[str, Any]] = []
        for row in rows:
            row_copy = copy.deepcopy(row)
            self._ensure_unique_constraints(row_copy)
            self._state[self._table_name].append(row_copy)
            inserted_rows.append(copy.deepcopy(row_copy))
        return inserted_rows

    def _update_rows(self) -> list[dict[str, Any]]:
        updated_rows: list[dict[str, Any]] = []
        for row in self._state[self._table_name]:
            if all(row.get(column) == value for column, value in self._filters):
                row.update(copy.deepcopy(self._payload))
                updated_rows.append(copy.deepcopy(row))
        return updated_rows

    def _delete_rows(self) -> list[dict[str, Any]]:
        deleted_rows: list[dict[str, Any]] = []
        remaining_rows: list[dict[str, Any]] = []
        for row in self._state[self._table_name]:
            if all(row.get(column) == value for column, value in self._filters):
                deleted_rows.append(copy.deepcopy(row))
            else:
                remaining_rows.append(row)

        self._state[self._table_name] = remaining_rows
        if self._table_name == "properties":
            deleted_property_ids = {row["id"] for row in deleted_rows}
            self._state["favorites"] = [
                row
                for row in self._state["favorites"]
                if row["property_id"] not in deleted_property_ids
            ]
        return deleted_rows

    def _ensure_unique_constraints(self, row: dict[str, Any]) -> None:
        if self._table_name == "properties":
            if any(existing_row["id"] == row["id"] for existing_row in self._state["properties"]):
                raise ValueError("Duplicate property id")
            return

        if self._table_name == "favorites":
            if any(
                existing_row["user_id"] == row["user_id"]
                and existing_row["property_id"] == row["property_id"]
                for existing_row in self._state["favorites"]
            ):
                raise ValueError("Duplicate favorite")


class FakeSupabaseClient:
    def __init__(self) -> None:
        self._state: dict[str, list[dict[str, Any]]] = {}
        self.reset()

    def table(self, table_name: str) -> FakeSupabaseTable:
        if table_name not in self._state:
            self._state[table_name] = []
        return FakeSupabaseTable(self._state, table_name)

    def reset(self) -> None:
        self._state = copy.deepcopy(_default_state())

    def replace_table(self, table_name: str, rows: Iterable[dict[str, Any]]) -> None:
        self._state[table_name] = [copy.deepcopy(row) for row in rows]

    def read_table(self, table_name: str) -> list[dict[str, Any]]:
        return [copy.deepcopy(row) for row in self._state.get(table_name, [])]


_fallback_client = FakeSupabaseClient()
_supabase_client: Optional[Union[SupabaseClient, FakeSupabaseClient]] = None
_supabase_config: Optional[tuple[Optional[str], Optional[str]]] = None


def _build_real_client() -> Optional[SupabaseClient]:
    if create_client is None:
        return None

    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_role_key:
        return None

    return create_client(supabase_url, service_role_key)


def get_supabase_client() -> Union[SupabaseClient, FakeSupabaseClient]:
    global _supabase_client
    global _supabase_config

    current_config = (
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    )

    if _supabase_client is None or _supabase_config != current_config:
        _supabase_client = _build_real_client() or _fallback_client
        _supabase_config = current_config

    return _supabase_client


def seed_fake_supabase(
    *,
    properties: Optional[Iterable[dict[str, Any]]] = None,
    favorites: Optional[Iterable[dict[str, Any]]] = None,
) -> None:
    if properties is None and favorites is None:
        _fallback_client.reset()
        return

    if properties is not None:
        _fallback_client.replace_table("properties", properties)
    if favorites is not None:
        _fallback_client.replace_table("favorites", favorites)
