from typing import Optional

from app.core.supabase import get_supabase_client, seed_fake_supabase
from app.schemas.property import Property


def _property_to_record(property_item: Property) -> dict[str, object]:
    return property_item.model_dump(mode="json")


def _property_from_record(record: dict[str, object]) -> Property:
    return Property(**record)


def _replace_all(properties: list[Property]) -> None:
    seed_fake_supabase(
        properties=[_property_to_record(property_item) for property_item in properties],
        favorites=[],
    )


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


class _PropertyStoreProxy:
    def __getitem__(self, item):
        return get_all()[item]

    def __iter__(self):
        return iter(get_all())

    def __len__(self) -> int:
        return len(get_all())

    def __setitem__(self, item, value) -> None:
        if isinstance(item, slice):
            if item.start is None and item.stop is None and item.step is None:
                _replace_all(list(value))
                return
            raise TypeError("Only full-slice assignment is supported")

        properties = get_all()
        properties[item] = value
        _replace_all(properties)

PROPERTIES = _PropertyStoreProxy()
