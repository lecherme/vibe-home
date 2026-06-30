import os
import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.v1.admin.router import router as admin_router
from app.api.v1.ai_search.router import router as ai_search_router
from app.api.v1.auth.router import auth_rate_limiter, router as auth_router
from app.api.v1.favorites.router import router as favorites_router
from app.api.v1.properties.router import router as properties_router
from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.logging import bind_request_id, clear_request_id, configure_logging

settings = get_settings()
configure_logging()
logger = logging.getLogger(__name__)


class _RequestIDMiddleware:
    """Pure ASGI middleware — passes every response chunk through immediately.

    BaseHTTPMiddleware (used by @app.middleware("http")) buffers streaming
    responses in an anyio memory channel, breaking SSE delivery timing.
    This implementation injects X-Request-ID only on the response-start
    message and forwards body chunks without any additional buffering.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid4())
        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["request_id"] = request_id  # type: ignore[index]
        token = bind_request_id(request_id)

        async def _send(message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Request-ID", request_id)
            await send(message)

        try:
            await self.app(scope, receive, _send)
        finally:
            clear_request_id(token)


def _get_cors_allowed_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS")
    if raw_origins:
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return settings.allowed_origins


cors_allowed_origins = _get_cors_allowed_origins()
cors_allowed_methods = ["GET", "POST", "PUT", "DELETE"]
cors_allowed_headers = ["Accept", "Authorization", "Content-Type"]

app = FastAPI(title="vibe_home backend")
app.state.auth_rate_limiter = auth_rate_limiter
app.state.limiter = auth_rate_limiter
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allowed_origins,
    allow_credentials=True,
    allow_methods=cors_allowed_methods,
    allow_headers=cors_allowed_headers,
)
app.add_middleware(_RequestIDMiddleware)


@app.on_event("startup")
async def log_application_startup() -> None:
    logger.info("Application startup complete")


app.include_router(api_router)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(favorites_router, prefix="/api/v1/favorites", tags=["favorites"])
app.include_router(properties_router, prefix="/api/v1/properties", tags=["properties"])
app.include_router(ai_search_router, prefix="/api/v1/search/ai", tags=["search"])
