from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_response_contains_x_request_id_header():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")
    assert response.headers["X-Request-ID"].strip() != ""


def test_client_provided_x_request_id_is_preserved():
    custom_request_id = "client-request-id-abc123"

    response = client.get("/health", headers={"X-Request-ID": custom_request_id})

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_request_id


def test_x_request_id_is_generated_when_header_is_missing():
    response = client.get("/health")

    request_id = response.headers.get("X-Request-ID")

    assert request_id is not None
    assert len(request_id) > 0


def test_health_endpoint_still_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
