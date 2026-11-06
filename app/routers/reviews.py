from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Restaurant, Review
from ..schemas import ReviewCreate, ReviewOut

router = APIRouter(prefix="/api/restaurants", tags=["reviews"])

@router.post("/{rid}/reviews", status_code=201, response_model=ReviewOut)
def create_review(rid: int, payload: ReviewCreate, db: Session = Depends(get_db)):
    restaurant = db.get(Restaurant, rid)
    if restaurant is None:
        return JSONResponse(status_code=404, content={"error": "restaurant not found"})

    review = Review(restaurant_id=rid, **payload.model_dump())
    db.add(review)
    try:
        db.flush()
        db.commit()
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=409,
            content={"error": "этот автор уже оставлял отзыв на этот ресторан", "field": "author"},
        )
    db.refresh(review)
    return review

@router.get("/{rid}/reviews", response_model=list[ReviewOut])
def list_reviews(rid: int, db: Session = Depends(get_db)):
    restaurant = db.get(Restaurant, rid)
    if restaurant is None:
        return JSONResponse(status_code=404, content={"error": "restaurant not found"})
    stmt = select(Review).where(Review.restaurant_id == rid).order_by(Review.id)
    return db.execute(stmt).scalars().all()