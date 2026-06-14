"""CI tests — health path defaults to /health (see HEALTH_PATH in .env for deploy)."""

from app.main import app


def test_health():
    """Verify /health returns 200 and the expected JSON body."""
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
