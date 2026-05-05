from app.core.supabase import get_supabase_client
from app.schemas.health import HealthResponse


def get_health_status() -> HealthResponse:
    try:
        client = get_supabase_client()
        client.table("properties").select("id").limit(1).execute()
    except Exception:
        return HealthResponse(status="error")

    return HealthResponse(status="ok")
