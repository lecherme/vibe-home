from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.admin.router import router as admin_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.favorites.router import router as favorites_router
from app.api.v1.properties.router import router as properties_router
from app.api.v1 import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="vibe_home backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(favorites_router, prefix="/api/v1/favorites", tags=["favorites"])
app.include_router(properties_router, prefix="/api/v1/properties", tags=["properties"])
