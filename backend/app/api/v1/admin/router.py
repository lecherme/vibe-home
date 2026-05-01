from fastapi import APIRouter, Depends, Response, status

from app.core.security import require_role
from app.schemas.admin import PropertyCreate, PropertyUpdate
from app.schemas.auth import UserRead
from app.schemas.property import Property as PropertyRead
from app.services.admin import create_property, delete_property, update_property


router = APIRouter()


@router.post("/properties", response_model=PropertyRead, status_code=status.HTTP_201_CREATED)
async def create_admin_property(
    data: PropertyCreate,
    current_user: UserRead = Depends(require_role("admin")),
) -> PropertyRead:
    del current_user
    return create_property(data)


@router.put("/properties/{property_id}", response_model=PropertyRead)
async def update_admin_property(
    property_id: str,
    data: PropertyUpdate,
    current_user: UserRead = Depends(require_role("admin")),
) -> PropertyRead:
    del current_user
    return update_property(property_id, data)


@router.delete("/properties/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_property(
    property_id: str,
    current_user: UserRead = Depends(require_role("admin")),
) -> Response:
    del current_user
    delete_property(property_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
