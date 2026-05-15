"""Application route and security tests."""

import pytest

from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True, ENVIRONMENT="testing", WTF_CSRF_ENABLED=False)
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Website CI/CD Pipeline" in response.data


def test_login_page_get(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign In" in response.data


def test_login_post_success(client):
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
    )
    assert response.status_code == 200
    assert b"Welcome" in response.data
    assert b"testuser" in response.data


def test_login_post_empty_fields(client):
    response = client.post("/login", data={"username": "", "password": ""})
    assert response.status_code == 200
    assert b"Please enter both" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "website-cicd-pipeline"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data


def test_health_live(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.get_json()["status"] == "alive"


def test_health_ready(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"app_info" in response.data


def test_security_headers(client):
    response = client.get("/")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_404_unknown_route(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
