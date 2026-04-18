import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    def _override():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override
    yield TestClient(app)
    app.dependency_overrides.clear()


SAMPLE = {
    "title": "Beach Condo",
    "description": "Ocean view",
    "price": 250000.0,
    "location": "Miami, FL",
    "area_sqm": 85.5,
    "bedrooms": 2,
    "bathrooms": 1,
    "property_type": "apartment",
    "is_for_rent": False,
    "owner_id": 1,
}


def _create(client: TestClient, **overrides):
    return client.post("/listings/", json={**SAMPLE, **overrides})


# ── Create ──────────────────────────────────────────────

def test_create_listing(client):
    resp = _create(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Beach Condo"
    assert data["id"] is not None
    assert "created_at" in data


def test_create_listing_minimal(client):
    resp = client.post("/listings/", json={
        "title": "Bare",
        "price": 100.0,
        "location": "Nowhere",
        "owner_id": 1,
    })
    assert resp.status_code == 201
    assert resp.json()["is_for_rent"] is True


def test_create_listing_missing_required(client):
    resp = client.post("/listings/", json={"title": "No price"})
    assert resp.status_code == 422


# ── Read ────────────────────────────────────────────────

def test_get_listing(client):
    created = _create(client).json()
    resp = client.get(f"/listings/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Beach Condo"


def test_get_listing_not_found(client):
    resp = client.get("/listings/999")
    assert resp.status_code == 404


def test_list_listings(client):
    _create(client, title="A")
    _create(client, title="B")
    resp = client.get("/listings/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_listings_pagination(client):
    for i in range(5):
        _create(client, title=f"L{i}")
    resp = client.get("/listings/?skip=2&limit=2")
    assert len(resp.json()) == 2


# ── Update ──────────────────────────────────────────────

def test_update_listing(client):
    created = _create(client).json()
    resp = client.patch(f"/listings/{created['id']}", json={"price": 300000.0})
    assert resp.status_code == 200
    assert resp.json()["price"] == 300000.0
    assert resp.json()["title"] == "Beach Condo"  # unchanged


def test_update_listing_not_found(client):
    resp = client.patch("/listings/999", json={"price": 1.0})
    assert resp.status_code == 404


# ── Delete ──────────────────────────────────────────────

def test_delete_listing(client):
    created = _create(client).json()
    resp = client.delete(f"/listings/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"/listings/{created['id']}").status_code == 404


def test_delete_listing_not_found(client):
    resp = client.delete("/listings/999")
    assert resp.status_code == 404
