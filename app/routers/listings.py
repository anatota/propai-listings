from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Listing, User
from app.schemas import ListingCreate, ListingUpdate, ListingResponse, ListingPage
from app.auth import get_current_user

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.get(
    "/",
    response_model=ListingPage,
    summary="List listings",
    description="Returns a paginated list of all listings. Supports optional filters for city, price range, property type, and rental status. No authentication required.",
)
def list_listings(
    city: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    property_type: str | None = None,
    is_for_rent: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Listing)
    if city is not None:
        q = q.filter(Listing.location.ilike(f"%{city}%"))
    if min_price is not None:
        q = q.filter(Listing.price >= min_price)
    if max_price is not None:
        q = q.filter(Listing.price <= max_price)
    if property_type is not None:
        q = q.filter(Listing.property_type == property_type)
    if is_for_rent is not None:
        q = q.filter(Listing.is_for_rent == is_for_rent)

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get(
    "/{listing_id}",
    response_model=ListingResponse,
    summary="Get a listing",
    description="Fetches a single listing by its ID. Returns 404 if the listing does not exist. No authentication required.",
)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.post(
    "/",
    response_model=ListingResponse,
    status_code=201,
    summary="Create a listing",
    description="Creates a new real estate listing owned by the authenticated user. Requires a valid Bearer token.",
)
def create_listing(
    payload: ListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    listing = Listing(**payload.model_dump(), owner_id=current_user.id)
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.patch(
    "/{listing_id}",
    response_model=ListingResponse,
    summary="Update a listing",
    description="Partially updates fields on an existing listing. Requires authentication and ownership; returns 403 if the requester is not the owner.",
)
def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this listing")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return listing


@router.delete(
    "/{listing_id}",
    status_code=204,
    summary="Delete a listing",
    description="Permanently deletes a listing by ID. Requires authentication and ownership; returns 403 if the requester is not the owner.",
)
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
    db.delete(listing)
    db.commit()
