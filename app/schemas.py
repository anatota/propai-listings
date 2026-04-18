from pydantic import BaseModel, ConfigDict
from datetime import datetime


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
    owner_id: int


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
