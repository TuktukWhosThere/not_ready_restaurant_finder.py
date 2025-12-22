# app/routes/restaurant_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api import fetch_restaurants
from app.schemas.restaurant import RestaurantRead

router = APIRouter()


@router.get("/", response_model=list[RestaurantRead])
def fetch_restaurants_endpoint(latitude: float, longitude: float, radius: int, user_id: int = None, db: Session = Depends(get_db)):
    return fetch_restaurants(latitude=latitude, longitude=longitude, radius=radius, user_id=user_id, db=db)
