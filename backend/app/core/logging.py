import json
import logging
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from typing import Optional


_request_id_context: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_context.get()
        return True


_EXTRA_FIELDS = (
    "parse_filters_ms",
    "interpret_needs_ms",
    "resolve_ids_ms",
    "collect_items_ms",
    "total_ms",
    "query",
)


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }
        for field in _EXTRA_FIELDS:
            val = getattr(record, field, None)
            if val is not None:
                payload[field] = val
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def bind_request_id(request_id: str) -> Token:
    return _request_id_context.set(request_id)


def clear_request_id(token: Token) -> None:
    _request_id_context.reset(token)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())
    handler.addFilter(RequestIdFilter())

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.propagate = True
