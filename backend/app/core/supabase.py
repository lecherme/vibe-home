import os
from typing import Any, Optional

try:
    from supabase import Client as SupabaseClient
    from supabase import create_client
except ImportError:  # pragma: no cover
    SupabaseClient = Any  # type: ignore[misc,assignment]
    create_client = None


_supabase_client: Optional[Any] = None
_supabase_config: Optional[tuple[Optional[str], Optional[str]]] = None


def _build_real_client() -> Optional[Any]:
    if create_client is None:
        return None

    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_role_key:
        return None

    return create_client(supabase_url, service_role_key)


def get_supabase_client() -> Any:
    global _supabase_client
    global _supabase_config

    current_config = (
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    )

    if _supabase_client is None or _supabase_config != current_config:
        client = _build_real_client()
        if client is None:
            raise RuntimeError(
                "Supabase client is not configured: SUPABASE_URL and "
                "SUPABASE_SERVICE_ROLE_KEY must be set"
            )
        _supabase_client = client
        _supabase_config = current_config

    return _supabase_client
