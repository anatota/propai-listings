from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


# ── User ────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


# ── Listing ─────────────────────────────────────────────

class ListingBase(BaseModel):
    title: str
    description: str | None = None
    price: float
    location: str
    area_sqm: float | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    property_type: str | None = None
    is_for_rent: bool = True


class ListingCreate(ListingBase):
    pass


class ListingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    location: str | None = None
    area_sqm: float | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    property_type: str | None = None
    is_for_rent: bool | None = None


class ListingResponse(ListingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime


class ListingPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ListingResponse]
