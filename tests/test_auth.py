import pytest
from fastapi.testclient import TestClient


def _register(client: TestClient, email="user@test.com", password="secret123"):
    return client.post("/auth/register", json={"email": email, "password": password})


def _login(client: TestClient, email="user@test.com", password="secret123"):
    return client.post("/auth/token", data={"username": email, "password": password})


# ── Register ────────────────────────────────────────────

def test_register(client):
    resp = _register(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "user@test.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    _register(client)
    resp = _register(client)
    assert resp.status_code == 400
    assert resp.json()["code"] == "BAD_REQUEST"


def test_register_invalid_email(client):
    resp = client.post("/auth/register", json={"email": "not-an-email", "password": "secret"})
    assert resp.status_code == 422


# ── Login ────────────────────────────────────────────────

def test_login(client):
    _register(client)
    resp = _login(client)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    _register(client)
    resp = _login(client, password="wrongpassword")
    assert resp.status_code == 401
    assert resp.json()["code"] == "UNAUTHORIZED"


def test_login_unknown_user(client):
    resp = _login(client, email="ghost@test.com")
    assert resp.status_code == 401


# ── Protected route ──────────────────────────────────────

def test_full_auth_flow(client):
    _register(client)
    token = _login(client).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post(
        "/listings/",
        json={"title": "Auth Test", "price": 100.0, "location": "Tbilisi"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Auth Test"


def test_invalid_token_rejected(client):
    resp = client.post(
        "/listings/",
        json={"title": "T", "price": 1.0, "location": "X"},
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 401


def test_missing_token_rejected(client):
    resp = client.post("/listings/", json={"title": "T", "price": 1.0, "location": "X"})
    assert resp.status_code == 401
