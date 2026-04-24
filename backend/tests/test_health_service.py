from app.services.health_service import get_health_status


def test_get_health_status_returns_ok() -> None:
    response = get_health_status()

    assert response.status == "ok"
