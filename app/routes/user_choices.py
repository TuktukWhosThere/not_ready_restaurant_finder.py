# app/routes/user_choices.py
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.api import suggest_restaurant, confirm_visit, deny_visit, update_visit
from app.schemas.restaurant import RestaurantRead
from app.schemas.visit import UserVisitRead, UserVisitUpdate

router = APIRouter(tags=["User Choices"])


# ---------------- Helpers ----------------
def get_current_user_id(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user_id


# ---------------- Suggest a Restaurant ----------------
@router.get("/suggest", response_model=RestaurantRead)
def suggest(
    request: Request,
    latitude: float,
    longitude: float,
    radius: int,
    strategy: str = "random",
    db: Session = Depends(get_db),
):
    user_id = get_current_user_id(request)

    restaurant = suggest_restaurant(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        strategy=strategy,
        db=db,
    )

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurants available",
        )

    return restaurant


# ---------------- Confirm a Visit ----------------
@router.post("/confirm/{restaurant_id}")
def confirm(
    request: Request,
    restaurant_id: int,
    latitude: float = Form(...),
    longitude: float = Form(...),
    radius: int = Form(...),
    strategy: str = Form("random"),
    db: Session = Depends(get_db),
):
    user_id = get_current_user_id(request)

    confirm_visit(user_id, restaurant_id, db)

    return RedirectResponse(
        url=(
            f"/user_choices/suggest?"
            f"latitude={latitude}"
            f"&longitude={longitude}"
            f"&radius={radius}"
            f"&strategy={strategy}"
        ),
        status_code=303,
    )


# ---------------- Deny / Forbid ----------------
@router.post("/deny/{restaurant_id}")
def deny(
    request: Request,
    restaurant_id: int,
    latitude: float = Form(...),
    longitude: float = Form(...),
    radius: int = Form(...),
    strategy: str = Form("random"),
    db: Session = Depends(get_db),
):
    user_id = get_current_user_id(request)

    deny_visit(user_id, restaurant_id, db)

    return RedirectResponse(
        url=(
            f"/user_choices/suggest?"
            f"latitude={latitude}"
            f"&longitude={longitude}"
            f"&radius={radius}"
            f"&strategy={strategy}"
        ),
        status_code=303,
    )


# ---------------- Update Visit ----------------
@router.patch("/update/{restaurant_id}", response_model=UserVisitRead)
def update(
    request: Request,
    restaurant_id: int,
    update_data: UserVisitUpdate,
    db: Session = Depends(get_db),
):
    user_id = get_current_user_id(request)

    return update_visit(
        user_id=user_id,
        restaurant_id=restaurant_id,
        visited=update_data.visited,
        forbidden=update_data.forbidden,
        rating=update_data.rating_given,
        db=db,
    )
