# app/schemas/restaurant.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RestaurantRead(BaseModel):
    id: int
    name: str
    place_id: str
    vicinity: Optional[str]
    rating: Optional[float]
    user_ratings: Optional[int]
    latitude: float
    longitude: float
    created_at: datetime

    class Config:
        from_attributes = True  # important for SQLAlchemy
