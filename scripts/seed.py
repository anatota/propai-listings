"""
Seed script — run from project root: python scripts/seed.py

Creates 1 admin user and 12 realistic property listings across Tbilisi and Batumi.
Idempotent: deletes all existing listings before inserting, upserts the admin user.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import User, Listing
from app.auth import hash_password

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

ADMIN_EMAIL = "admin@propai.ge"
ADMIN_PASSWORD = "Admin1234!"

LISTINGS = [
    # ── Tbilisi ─────────────────────────────────────────────────────────────
    {
        "title": "Sunny 2BR Apartment in Vake",
        "description": (
            "Well-maintained apartment on the 5th floor of a brick building in the heart of Vake. "
            "Close to Vake Park, international schools, and major supermarkets. "
            "Renovated kitchen, double-glazed windows, and a small balcony overlooking a quiet courtyard."
        ),
        "price": 1_200.0,
        "location": "Tbilisi, Vake, Paliashvili Street 45",
        "area_sqm": 72.0,
        "bedrooms": 2,
        "bathrooms": 1,
        "property_type": "apartment",
        "is_for_rent": True,
    },
    {
        "title": "Spacious 3BR Apartment for Sale – Saburtalo",
        "description": (
            "Bright three-bedroom apartment on Vazha-Pshavela Avenue with an open-plan living area "
            "and recently upgraded plumbing and electrics. Five-minute walk to Delisi metro station "
            "and within the Saburtalo school district."
        ),
        "price": 148_000.0,
        "location": "Tbilisi, Saburtalo, Vazha-Pshavela Avenue 12",
        "area_sqm": 98.0,
        "bedrooms": 3,
        "bathrooms": 2,
        "property_type": "apartment",
        "is_for_rent": False,
    },
    {
        "title": "Studio Apartment in Old Town Tbilisi",
        "description": (
            "Charming studio in a restored 19th-century building in Abanotubani. "
            "Exposed brick walls, wooden ceilings, and a private terrace with a view of the "
            "Metekhi Church. Ideal for short or long-term rental."
        ),
        "price": 750.0,
        "location": "Tbilisi, Abanotubani, Gorgasali Street 8",
        "area_sqm": 38.0,
        "bedrooms": 1,
        "bathrooms": 1,
        "property_type": "apartment",
        "is_for_rent": True,
    },
    {
        "title": "Modern 1BR Near Rustaveli – Long-Term",
        "description": (
            "Fully furnished one-bedroom apartment two blocks from Rustaveli Avenue. "
            "Air-conditioned, fibre internet included, secure parking available. "
            "Ideal for professionals and expats."
        ),
        "price": 900.0,
        "location": "Tbilisi, Mtatsminda, Kostava Street 31",
        "area_sqm": 55.0,
        "bedrooms": 1,
        "bathrooms": 1,
        "property_type": "apartment",
        "is_for_rent": True,
    },
    {
        "title": "Private House with Garden – Digomi",
        "description": (
            "Detached two-storey house on a 400 sqm plot in Digomi. "
            "Four bedrooms, a large covered terrace, and a fruit garden. "
            "Recently re-roofed and replumbed; gas central heating."
        ),
        "price": 210_000.0,
        "location": "Tbilisi, Digomi, 8th Micro-District Lane 3",
        "area_sqm": 165.0,
        "bedrooms": 4,
        "bathrooms": 2,
        "property_type": "house",
        "is_for_rent": False,
    },
    {
        "title": "Commercial Office Space – Vera District",
        "description": (
            "Open-plan office unit on the ground floor of a mixed-use building on Ilia Chavchavadze Avenue. "
            "180 sqm divisible into up to three offices. High foot traffic, dedicated parking, and "
            "24/7 access control."
        ),
        "price": 3_500.0,
        "location": "Tbilisi, Vera, Chavchavadze Avenue 57",
        "area_sqm": 180.0,
        "bedrooms": None,
        "bathrooms": 2,
        "property_type": "commercial",
        "is_for_rent": True,
    },
    {
        "title": "Renovated 4BR House for Sale – Nutsubidze Plateau",
        "description": (
            "Fully renovated house spread across three floors in the quiet Nutsubidze Plateau area. "
            "Underfloor heating, fitted wardrobes, and a rooftop terrace with panoramic city views. "
            "Garage for two cars included."
        ),
        "price": 320_000.0,
        "location": "Tbilisi, Nutsubidze Plateau, 3rd Nutsubidze Street 14",
        "area_sqm": 220.0,
        "bedrooms": 4,
        "bathrooms": 3,
        "property_type": "house",
        "is_for_rent": False,
    },
    {
        "title": "Retail Unit on Agmashenebeli Avenue",
        "description": (
            "Street-facing retail unit on one of Tbilisi's busiest commercial corridors. "
            "Large display window, storage room at rear, and mezzanine level. "
            "Suitable for café, boutique, or services business."
        ),
        "price": 280_000.0,
        "location": "Tbilisi, Didube, Agmashenebeli Avenue 104",
        "area_sqm": 95.0,
        "bedrooms": None,
        "bathrooms": 1,
        "property_type": "commercial",
        "is_for_rent": False,
    },
    # ── Batumi ──────────────────────────────────────────────────────────────
    {
        "title": "Sea-View Apartment – Batumi Boulevard",
        "description": (
            "Furnished one-bedroom apartment on the 12th floor with unobstructed Black Sea views "
            "from the living room and bedroom. Walking distance to the beach, casino strip, and "
            "central market. High rental yield property."
        ),
        "price": 130_000.0,
        "location": "Batumi, Boulevard District, Ninoshvili Street 22",
        "area_sqm": 52.0,
        "bedrooms": 1,
        "bathrooms": 1,
        "property_type": "apartment",
        "is_for_rent": False,
    },
    {
        "title": "2BR Apartment for Rent – Batumi New District",
        "description": (
            "Modern two-bedroom apartment in the New District with mountain views from the back balcony. "
            "24-hour concierge, rooftop pool access, and underground parking included in the rent."
        ),
        "price": 1_100.0,
        "location": "Batumi, New District, Sherif Khimshiashvili Street 7",
        "area_sqm": 78.0,
        "bedrooms": 2,
        "bathrooms": 1,
        "property_type": "apartment",
        "is_for_rent": True,
    },
    {
        "title": "Beachfront Commercial Unit – Batumi",
        "description": (
            "Ground-floor commercial unit 50 metres from the seafront promenade. "
            "Previously operated as a café; kitchen infrastructure in place. "
            "High summer footfall; long-term lease preferred."
        ),
        "price": 2_800.0,
        "location": "Batumi, Seaside, Rustaveli Avenue 3",
        "area_sqm": 110.0,
        "bedrooms": None,
        "bathrooms": 1,
        "property_type": "commercial",
        "is_for_rent": True,
    },
    {
        "title": "Cottage-Style House for Sale – Makhinjauri",
        "description": (
            "Three-bedroom cottage surrounded by subtropical greenery in the Makhinjauri suburb of Batumi. "
            "Large wraparound veranda, private well, and a vegetable garden. "
            "Quiet residential street, 10 minutes from the city centre by car."
        ),
        "price": 175_000.0,
        "location": "Batumi, Makhinjauri, Seaside Lane 5",
        "area_sqm": 130.0,
        "bedrooms": 3,
        "bathrooms": 2,
        "property_type": "house",
        "is_for_rent": False,
    },
]

# ---------------------------------------------------------------------------
# Seed logic
# ---------------------------------------------------------------------------

def seed():
    db = SessionLocal()
    try:
        # Ensure tables exist (safe no-op if they already do)
        Base.metadata.create_all(bind=engine)

        # Upsert admin user
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if admin:
            print(f"[skip]   admin user already exists  ({ADMIN_EMAIL})")
        else:
            admin = User(email=ADMIN_EMAIL, hashed_password=hash_password(ADMIN_PASSWORD))
            db.add(admin)
            db.flush()  # get admin.id before inserting listings
            print(f"[create] admin user  →  {ADMIN_EMAIL}")

        # Clear existing listings (idempotent)
        deleted = db.query(Listing).delete()
        if deleted:
            print(f"[clear]  removed {deleted} existing listing(s)")

        # Insert listings
        for data in LISTINGS:
            listing = Listing(**data, owner_id=admin.id)
            db.add(listing)
            db.flush()
            flag = "rental" if data["is_for_rent"] else "sale"
            print(f"[create] [{flag:<6}] {data['title']}")

        db.commit()
        print(f"\nDone — {len(LISTINGS)} listings seeded.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
