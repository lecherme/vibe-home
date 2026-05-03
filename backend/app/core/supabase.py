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
        self._state: dict[str, list[dict[str, Any]]] = {
            "properties": [],
            "favorites": [],
        }

    def table(self, table_name: str) -> FakeSupabaseTable:
        if table_name not in self._state:
            self._state[table_name] = []
        return FakeSupabaseTable(self._state, table_name)

    def replace_table(self, table_name: str, rows: Iterable[dict[str, Any]]) -> None:
        self._state[table_name] = [copy.deepcopy(row) for row in rows]

    def read_table(self, table_name: str) -> list[dict[str, Any]]:
        return [copy.deepcopy(row) for row in self._state.get(table_name, [])]


_fallback_client = FakeSupabaseClient()
_supabase_client: Optional[Union[SupabaseClient, FakeSupabaseClient]] = None


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

    if _supabase_client is None:
        _supabase_client = _build_real_client() or _fallback_client

    return _supabase_client


def seed_fake_supabase(
    *,
    properties: Optional[Iterable[dict[str, Any]]] = None,
    favorites: Optional[Iterable[dict[str, Any]]] = None,
) -> None:
    if properties is not None:
        _fallback_client.replace_table("properties", properties)
    if favorites is not None:
        _fallback_client.replace_table("favorites", favorites)
