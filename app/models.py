from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    Index,
    CheckConstraint,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    cuisine: Mapped[str] = mapped_column(String(100), nullable=False)

    reviews: Mapped[list["Review"]] = relationship(
        back_populates="restaurant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
    Index(
        "ix_restaurants_title_lower",
        func.lower(title),
        postgresql_ops={"lower": "text_pattern_ops"},
    ),
)


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    restaurant: Mapped[Restaurant] = relationship(back_populates="reviews")

    __table_args__ = (
        UniqueConstraint("restaurant_id", "author", name="uq_reviews_restaurant_author"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
    )