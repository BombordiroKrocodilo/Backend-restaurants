from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session
from typing import Optional

from ..db import get_db
from ..models import Restaurant, Review
from ..schemas import RestaurantCreate, RestaurantUpdate, RestaurantOut

router = APIRouter(prefix="/api/restaurants", tags=["restaurants"])

@router.post("", status_code=201, response_model=RestaurantOut)
def create_restaurant(payload: RestaurantCreate, db: Session = Depends(get_db)):
    r = Restaurant(**payload.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.get("", response_model=list[RestaurantOut])
def list_restaurants(
    limit: Optional[int] = None,
    offset: int = 0,
    cuisine: Optional[str] = None,
    q: Optional[str] = Query(None, description="Поиск по названию без учёта регистра"),
    db: Session = Depends(get_db),
):
    stmt = select(Restaurant)
    if cuisine is not None:
        stmt = stmt.where(Restaurant.cuisine == cuisine)
    if q:
        stmt = stmt.where(func.lower(Restaurant.title).like(f"{q.lower()}%"))
    stmt = stmt.order_by(Restaurant.id).offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)
    return db.execute(stmt).scalars().all()

@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            Restaurant.id,
            Restaurant.title,
            func.count(Review.id).label("reviews_count"),
            func.avg(Review.rating).label("avg_rating"),
        )
        .outerjoin(Review, Review.restaurant_id == Restaurant.id)
        .group_by(Restaurant.id, Restaurant.title)
        .order_by(Restaurant.id)
    ).all()
    return [
        {
            "restaurant_id": r.id,
            "title": r.title,
            "reviews_count": int(r.reviews_count or 0),
            "avg_rating": float(r.avg_rating) if r.avg_rating is not None else None,
        }
        for r in rows
    ]

@router.get("/{rid}", response_model=RestaurantOut)
def get_restaurant(rid: int, db: Session = Depends(get_db)):
    r = db.get(Restaurant, rid)
    if r is None:
        return JSONResponse(status_code=404, content={"error": "not found"})
    return r

@router.patch("/{rid}", response_model=RestaurantOut)
def update_restaurant(rid: int, payload: RestaurantUpdate, db: Session = Depends(get_db)):
    r = db.get(Restaurant, rid)
    if r is None:
        return JSONResponse(status_code=404, content={"error": "not found"})
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r

@router.put("/{rid}", response_model=RestaurantOut)
def replace_restaurant(rid: int, payload: RestaurantCreate, db: Session = Depends(get_db)):
    r = db.get(Restaurant, rid)
    if r is None:
        return JSONResponse(status_code=404, content={"error": "not found"})
    for k, v in payload.model_dump().items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r

@router.delete("/{rid}", status_code=204)
def delete_restaurant(rid: int, db: Session = Depends(get_db)):
    r = db.get(Restaurant, rid)
    if r is None:
        return JSONResponse(status_code=404, content={"error": "not found"})
    db.delete(r)
    db.commit()
    return Response(status_code=204)