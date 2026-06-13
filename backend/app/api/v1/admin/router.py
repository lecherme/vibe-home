from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status

from app.core.security import require_role
from app.core.supabase import get_supabase_client
from app.data.properties import get_all
from app.schemas.admin import PropertyCreate, PropertyUpdate
from app.schemas.auth import UserRead
from app.schemas.property import Property as PropertyRead
from app.services.admin import create_property, delete_property, update_property
from app.services.embeddings.service import try_upsert_property_embedding


router = APIRouter()

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_CONTENT_TYPE_TO_EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
_MAX_FILE_SIZE = 5 * 1024 * 1024
_STORAGE_BUCKET = "vibe_home"


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


@router.post("/embeddings/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync_property_embeddings(
    current_user: UserRead = Depends(require_role("admin")),
) -> dict[str, int]:
    del current_user

    properties = get_all()
    for property_item in properties:
        try_upsert_property_embedding(
            property_id=property_item.id,
            title=property_item.title,
            description=property_item.description,
            location=property_item.location,
            area_sqm=property_item.area_sqm,
            built_year=property_item.built_year,
            subway_distance_m=property_item.subway_distance_m,
            tags=property_item.tags,
        )

    return {"synced": len(properties)}


@router.delete("/properties/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_property(
    property_id: str,
    current_user: UserRead = Depends(require_role("admin")),
) -> Response:
    del current_user
    delete_property(property_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/uploads/property-image")
async def upload_property_image(
    file: UploadFile = File(...),
    current_user: UserRead = Depends(require_role("admin")),
) -> dict[str, str]:
    del current_user

    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported file type")

    data = await file.read()
    if len(data) > _MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")

    ext = _CONTENT_TYPE_TO_EXT[file.content_type]
    path = f"properties/{uuid4()}.{ext}"
    sb = get_supabase_client()
    sb.storage.from_(_STORAGE_BUCKET).upload(
        path=path,
        file=data,
        file_options={"content-type": file.content_type},
    )
    url = sb.storage.from_(_STORAGE_BUCKET).get_public_url(path)
    return {"url": url}
