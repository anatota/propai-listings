from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Listing
from app.schemas import ListingCreate, ListingUpdate, ListingResponse

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/", response_model=list[ListingResponse])
def list_listings(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Listing).offset(skip).limit(limit).all()


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.post("/", response_model=ListingResponse, status_code=201)
def create_listing(payload: ListingCreate, db: Session = Depends(get_db)):
    listing = Listing(**payload.model_dump())
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.patch("/{listing_id}", response_model=ListingResponse)
def update_listing(listing_id: int, payload: ListingUpdate, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return listing


@router.delete("/{listing_id}", status_code=204)
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    db.delete(listing)
    db.commit()
