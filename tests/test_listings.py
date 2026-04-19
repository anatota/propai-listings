import pytest
from fastapi.testclient import TestClient

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
}


def _create(client: TestClient, headers: dict, **overrides):
    return client.post("/listings/", json={**SAMPLE, **overrides}, headers=headers)


# ── Create ──────────────────────────────────────────────

def test_create_listing(auth):
    client, headers = auth
    resp = _create(client, headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Beach Condo"
    assert data["id"] is not None
    assert "created_at" in data
    assert "owner_id" in data


def test_create_listing_minimal(auth):
    client, headers = auth
    resp = client.post(
        "/listings/",
        json={"title": "Bare", "price": 100.0, "location": "Nowhere"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["is_for_rent"] is True


def test_create_listing_missing_required(auth):
    client, headers = auth
    resp = client.post("/listings/", json={"title": "No price"}, headers=headers)
    assert resp.status_code == 422


def test_create_listing_unauthenticated(client):
    resp = client.post("/listings/", json=SAMPLE)
    assert resp.status_code == 401


# ── Read ────────────────────────────────────────────────

def test_get_listing(auth):
    client, headers = auth
    created = _create(client, headers).json()
    resp = client.get(f"/listings/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Beach Condo"


def test_get_listing_not_found(client):
    resp = client.get("/listings/999")
    assert resp.status_code == 404


def test_list_listings(auth):
    client, headers = auth
    _create(client, headers, title="A")
    _create(client, headers, title="B")
    resp = client.get("/listings/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_listings_pagination(auth):
    client, headers = auth
    for i in range(5):
        _create(client, headers, title=f"L{i}")
    resp = client.get("/listings/?page=2&page_size=2")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["page"] == 2


# ── Filters ─────────────────────────────────────────────

def test_filter_by_city(auth):
    client, headers = auth
    _create(client, headers, title="Tbilisi Apt", location="Tbilisi, Georgia")
    _create(client, headers, title="Batumi House", location="Batumi, Georgia")
    resp = client.get("/listings/?city=tbilisi")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Tbilisi Apt"


def test_filter_by_price_range(auth):
    client, headers = auth
    _create(client, headers, title="Cheap", price=500.0)
    _create(client, headers, title="Mid", price=1000.0)
    _create(client, headers, title="Expensive", price=5000.0)
    resp = client.get("/listings/?min_price=600&max_price=2000")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Mid"


def test_filter_by_property_type(auth):
    client, headers = auth
    _create(client, headers, title="Apt", property_type="apartment")
    _create(client, headers, title="House", property_type="house")
    resp = client.get("/listings/?property_type=house")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "House"


def test_filter_by_is_for_rent(auth):
    client, headers = auth
    _create(client, headers, title="For Rent", is_for_rent=True)
    _create(client, headers, title="For Sale", is_for_rent=False)
    resp = client.get("/listings/?is_for_rent=true")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "For Rent"


def test_combined_filters(auth):
    client, headers = auth
    _create(client, headers, title="Match", location="Tbilisi, Georgia", property_type="apartment", price=800.0, is_for_rent=True)
    _create(client, headers, title="Wrong City", location="Batumi, Georgia", property_type="apartment", price=800.0, is_for_rent=True)
    _create(client, headers, title="Wrong Type", location="Tbilisi, Georgia", property_type="house", price=800.0, is_for_rent=True)
    resp = client.get("/listings/?city=tbilisi&property_type=apartment&is_for_rent=true")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Match"


# ── Update ──────────────────────────────────────────────

def test_update_listing(auth):
    client, headers = auth
    created = _create(client, headers).json()
    resp = client.patch(f"/listings/{created['id']}", json={"price": 300000.0}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["price"] == 300000.0
    assert resp.json()["title"] == "Beach Condo"


def test_update_listing_not_found(auth):
    client, headers = auth
    resp = client.patch("/listings/999", json={"price": 1.0}, headers=headers)
    assert resp.status_code == 404


def test_update_listing_unauthenticated(auth):
    client, headers = auth
    created = _create(client, headers).json()
    resp = client.patch(f"/listings/{created['id']}", json={"price": 1.0})
    assert resp.status_code == 401


def test_update_listing_wrong_owner(auth, other_auth):
    client, headers = auth
    _, other_headers = other_auth
    created = _create(client, headers).json()
    resp = client.patch(f"/listings/{created['id']}", json={"price": 1.0}, headers=other_headers)
    assert resp.status_code == 403


# ── Delete ──────────────────────────────────────────────

def test_delete_listing(auth):
    client, headers = auth
    created = _create(client, headers).json()
    resp = client.delete(f"/listings/{created['id']}", headers=headers)
    assert resp.status_code == 204
    assert client.get(f"/listings/{created['id']}").status_code == 404


def test_delete_listing_not_found(auth):
    client, headers = auth
    resp = client.delete("/listings/999", headers=headers)
    assert resp.status_code == 404


def test_delete_listing_unauthenticated(auth):
    client, headers = auth
    created = _create(client, headers).json()
    resp = client.delete(f"/listings/{created['id']}")
    assert resp.status_code == 401


def test_delete_listing_wrong_owner(auth, other_auth):
    client, headers = auth
    _, other_headers = other_auth
    created = _create(client, headers).json()
    resp = client.delete(f"/listings/{created['id']}", headers=other_headers)
    assert resp.status_code == 403
