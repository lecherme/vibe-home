from typing import Optional

from app.core.supabase import get_supabase_client
from app.schemas.property import Property


def _property_from_record(record: dict[str, object]) -> Property:
    return Property(**record)


def get_all() -> list[Property]:
    response = get_supabase_client().table("properties").select("*").execute()
    return [_property_from_record(record) for record in response.data]


def get_by_id(id: str) -> Optional[Property]:
    response = (
        get_supabase_client()
        .table("properties")
        .select("*")
        .eq("id", id)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    return _property_from_record(response.data[0])
