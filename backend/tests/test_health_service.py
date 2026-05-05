from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.health import router as health_router
from app.services.health_service import get_health_status


def test_get_health_status_returns_ok_for_configured_reachable_supabase(monkeypatch) -> None:
    class HealthyTable:
        def select(self, columns: str):
            del columns
            return self

        def limit(self, count: int):
            del count
            return self

        def execute(self):
            return None

    class HealthyClient:
        def table(self, table_name: str):
            del table_name
            return HealthyTable()

    monkeypatch.setattr(
        "app.services.health_service.get_supabase_client",
        lambda: HealthyClient(),
    )

    response = get_health_status()

    assert response.status == "ok"


def test_get_health_status_returns_error_when_supabase_is_unconfigured(monkeypatch) -> None:
    def _raise() -> None:
        raise RuntimeError("Supabase not configured")

    monkeypatch.setattr(
        "app.services.health_service.get_supabase_client",
        _raise,
    )

    response = get_health_status()

    assert response.status == "error"


def test_get_health_status_returns_error_when_supabase_is_unreachable(monkeypatch) -> None:
    class FailingTable:
        def select(self, columns: str):
            del columns
            return self

        def limit(self, count: int):
            del count
            return self

        def execute(self):
            raise RuntimeError("supabase unreachable")

    class FailingClient:
        def table(self, table_name: str):
            del table_name
            return FailingTable()

    monkeypatch.setattr(
        "app.services.health_service.get_supabase_client",
        lambda: FailingClient(),
    )

    response = get_health_status()

    assert response.status == "error"


def test_health_endpoint_returns_503_when_supabase_is_unreachable(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(health_router)

    monkeypatch.setattr(
        "app.api.v1.health.get_health_status",
        lambda: type("HealthResult", (), {"status": "error", "model_dump": lambda self: {"status": "error"}})(),
    )

    response = TestClient(app).get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "error"}
