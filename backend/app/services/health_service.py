from app.core.supabase import FakeSupabaseClient, get_supabase_client
from app.schemas.health import HealthResponse


def get_health_status() -> HealthResponse:
    try:
        supabase_client = get_supabase_client()
        if isinstance(supabase_client, FakeSupabaseClient):
            return HealthResponse(status="error")

        supabase_client.table("properties").select("id").limit(1).execute()
    except Exception:
        return HealthResponse(status="error")

    return HealthResponse(status="ok")
