from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth.router import router as auth_router
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
