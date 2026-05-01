from app.schemas.admin import PropertyCreate, PropertyUpdate
from app.schemas.property import Property as PropertyRead


def create_property(data: PropertyCreate) -> PropertyRead:
    ...


def update_property(property_id: str, data: PropertyUpdate) -> PropertyRead:
    ...


def delete_property(property_id: str) -> None:
    ...
