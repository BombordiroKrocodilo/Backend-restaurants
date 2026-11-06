from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class RestaurantCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=200)
    cuisine: str = Field(..., min_length=1, max_length=100)

    @field_validator("title", "address", "cuisine")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("поле не может быть пустым")
        return v

class RestaurantUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, min_length=1, max_length=200)
    cuisine: Optional[str] = Field(None, min_length=1, max_length=100)

    @field_validator("title", "address", "cuisine")
    @classmethod
    def not_blank(cls, v):
        if v is not None and not v.strip():
            raise ValueError("поле не может быть пустым")
        return v

class RestaurantOut(BaseModel):
    id: int
    title: str
    address: str
    cuisine: str
    model_config = {"from_attributes": True}

class ReviewCreate(BaseModel):
    author: str = Field(..., min_length=1, max_length=120)
    rating: int = Field(..., ge=1, le=5)
    text: str = Field(..., min_length=1, max_length=1000)

    @field_validator("author", "text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("поле не может быть пустым")
        return v

class ReviewOut(BaseModel):
    id: int
    restaurant_id: int
    author: str
    rating: int
    text: str
    created_at: datetime
    model_config = {"from_attributes": True}