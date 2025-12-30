# app/api.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .models import Restaurant, ApiCall
import requests
import os
from geopy.distance import geodesic
from math import sqrt
from sqlalchemy import and_
from sqlalchemy import or_
from app.models import UserVisit



API_KEY = os.getenv("API_KEY")

# ------------------- Restaurant Business Logic -------------------

def get_nearby_restaurants_from_api(latitude: float, longitude: float, radius: int):
    url = (
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={latitude},{longitude}"
        f"&radius={radius}"
        f"&type=restaurant"
        f"&key={API_KEY}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch data from Google Places API."}

def are_coordinates_within_combined_radius(latitude, longitude, radius, existing_calls):
    """Check if the current request is already covered by existing calls."""
    for call in existing_calls:
        distance = geodesic((latitude, longitude), (call.latitude, call.longitude)).meters
        if distance + radius <= call.radius:
            return True
    return False

def fetch_restaurants(
    latitude: float,
    longitude: float,
    radius: int,
    db: Session,
    user_id: int | None = None,
):
    # Load recent API calls (restaurants only)
    recent_calls = db.query(ApiCall).filter(
        and_(
            ApiCall.place_type == "restaurants",
            ApiCall.created_at >= datetime.utcnow() - timedelta(days=1),
        )
    ).all()

    # If already covered, return cached restaurants
    if are_coordinates_within_combined_radius(latitude, longitude, radius, recent_calls):
        radius_deg = radius / 111_000  # meters → degrees
        return db.query(Restaurant).filter(
            Restaurant.latitude.between(latitude - radius_deg, latitude + radius_deg),
            Restaurant.longitude.between(longitude - radius_deg, longitude + radius_deg),
        ).all()

    # Fetch new data from Google API
    data = get_nearby_restaurants_from_api(latitude, longitude, radius)
    if "results" not in data:
        return []

    restaurants_added = []
    restaurants_place_ids = []

    for r in data["results"]:
        # ✅ SAFETY CHECK — ONLY RESTAURANTS
        if "restaurant" not in r.get("types", []):
            continue

        restaurants_place_ids.append(r["place_id"])

        exists = db.query(Restaurant).filter(
            Restaurant.place_id == r["place_id"]
        ).first()

        if exists:
            continue

        restaurant = Restaurant(
            name=r.get("name"),
            place_id=r["place_id"],
            vicinity=r.get("vicinity"),
            rating=r.get("rating"),
            user_ratings=r.get("user_ratings_total"),
            latitude=r["geometry"]["location"]["lat"],
            longitude=r["geometry"]["location"]["lng"],
        )

        db.add(restaurant)
        restaurants_added.append(restaurant)

    # Log API call AFTER filtering
    api_call = ApiCall(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        result_count=len(restaurants_place_ids),
        place_type="restaurants",
    )
    db.add(api_call)

    db.commit()

    # Return only restaurants from this call
    if not restaurants_place_ids:
        return []

    return db.query(Restaurant).filter(
        Restaurant.place_id.in_(restaurants_place_ids)
    ).all()



# app/api.py
def suggest_restaurant(user_id: int, latitude: float, longitude: float, radius: int, strategy: str = "random", db: Session = None):
    if db is None:
        raise ValueError("Database session is required")

    # 1️⃣ Fetch all restaurants in the radius from DB (excluding visited/forbidden)
    excluded = db.query(UserVisit.restaurant_id).filter(
        UserVisit.user_id == user_id,
        or_(UserVisit.visited == True, UserVisit.forbidden == True)
    ).subquery()

    available = db.query(Restaurant).filter(
        ~Restaurant.id.in_(excluded)
    ).all()

    # Filter by radius
    available = [
        r for r in available
        if geodesic((latitude, longitude), (r.latitude, r.longitude)).meters <= radius
    ]

    # 2️⃣ If none available, fetch from Google API and update DB
    if not available:
        new_restaurants = fetch_restaurants(latitude, longitude, radius, db, user_id=user_id)
        available = [
            r for r in new_restaurants
            if r.id not in [ex[0] for ex in db.query(UserVisit.restaurant_id).filter(UserVisit.user_id==user_id)]
            and geodesic((latitude, longitude), (r.latitude, r.longitude)).meters <= radius
        ]

    if not available:
        return None

    # 3️⃣ Pick based on strategy
    if strategy == "random":
        import random
        return random.choice(available)
    elif strategy == "best_rated":
        available.sort(key=lambda r: r.rating or 0, reverse=True)
        return available[0]
    elif strategy == "closest":
        available.sort(key=lambda r: geodesic((latitude, longitude), (r.latitude, r.longitude)).meters)
        return available[0]
    else:
        return available[0]



def confirm_visit(user_id: int, restaurant_id: int, db: Session):
    visit = db.query(UserVisit).filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
    if not visit:
        visit = UserVisit(user_id=user_id, restaurant_id=restaurant_id, visited=True)
        db.add(visit)
    else:
        visit.visited = True
    db.commit()
    return visit

def deny_visit(user_id: int, restaurant_id: int, db: Session):
    visit = db.query(UserVisit).filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
    if not visit:
        visit = UserVisit(user_id=user_id, restaurant_id=restaurant_id, visited=False, forbidden=True)
        db.add(visit)
    else:
        visit.forbidden = True
    db.commit()
    return visit



def update_visit(user_id: int, restaurant_id: int, visited: bool = None, forbidden: bool = None, rating: float = None, db: Session = None):
    visit = db.query(UserVisit).filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
    if not visit:
        visit = UserVisit(user_id=user_id, restaurant_id=restaurant_id)
        db.add(visit)
    if visited is not None:
        visit.visited = visited
    if forbidden is not None:
        visit.forbidden = forbidden
    if rating is not None:
        visit.rating_given = rating
    db.commit()
    return visit
