import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "sqlite:///./unused.db")

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


@pytest.fixture()
def auth(client: TestClient):
    """Register a user and return (client, auth_headers)."""
    client.post("/auth/register", json={"email": "owner@test.com", "password": "secret123"})
    resp = client.post(
        "/auth/token",
        data={"username": "owner@test.com", "password": "secret123"},
    )
    token = resp.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def other_auth(client: TestClient):
    """Register a second user and return (client, auth_headers)."""
    client.post("/auth/register", json={"email": "other@test.com", "password": "secret123"})
    resp = client.post(
        "/auth/token",
        data={"username": "other@test.com", "password": "secret123"},
    )
    token = resp.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}
