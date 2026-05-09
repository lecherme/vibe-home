import inspect
import os
import re
import time
from collections import deque
from collections.abc import Awaitable, Callable
from functools import wraps
from threading import Lock
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.security import get_current_user
from app.schemas.auth import UserRead


router = APIRouter()


class AuthRateLimiter:
    _WINDOW_SECONDS = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
    }

    def __init__(self) -> None:
        self._requests: dict[tuple[str, str], deque[float]] = {}
        self._lock = Lock()

    def limit(self, rate_limit_provider: Callable[[], str]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(endpoint: Callable[..., Any]) -> Callable[..., Any]:
            signature = inspect.signature(endpoint)

            @wraps(endpoint)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                bound_arguments = signature.bind_partial(*args, **kwargs)
                request = bound_arguments.arguments.get("request")
                if not isinstance(request, Request):
                    raise RuntimeError("Rate-limited auth endpoints must accept a request parameter")

                limiter = getattr(request.app.state, "auth_rate_limiter", self)
                limiter.check(request, rate_limit_provider())

                result = endpoint(*args, **kwargs)
                if inspect.isawaitable(result):
                    return await cast(Awaitable[Any], result)
                return result

            wrapper.__signature__ = signature
            return wrapper

        return decorator

    def check(self, request: Request, rate_limit: str) -> None:
        max_requests, window_seconds = self._parse_rate_limit(rate_limit)
        now = time.monotonic()
        bucket_key = (self._client_identifier(request), request.url.path)

        with self._lock:
            request_times = self._requests.setdefault(bucket_key, deque())
            cutoff = now - window_seconds

            while request_times and request_times[0] <= cutoff:
                request_times.popleft()

            if len(request_times) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )

            request_times.append(now)

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()

    def _client_identifier(self, request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        if request.client is not None and request.client.host:
            return request.client.host

        return "anonymous"

    def _parse_rate_limit(self, rate_limit: str) -> tuple[int, int]:
        match = re.fullmatch(r"\s*(\d+)\s*/\s*(second|minute|hour|day)s?\s*", rate_limit.lower())
        if match is None:
            raise RuntimeError(
                "RATE_LIMIT_AUTH must use the format '<count>/<second|minute|hour|day>'",
            )

        count = int(match.group(1))
        unit = match.group(2)
        return count, self._WINDOW_SECONDS[unit]


def get_auth_rate_limit() -> str:
    return os.getenv("RATE_LIMIT_AUTH", "5/minute")


auth_rate_limiter = AuthRateLimiter()


@router.get("/me", response_model=UserRead)
@auth_rate_limiter.limit(get_auth_rate_limit)
async def read_current_user(
    request: Request,
    current_user: UserRead = Depends(get_current_user),
) -> UserRead:
    return current_user
