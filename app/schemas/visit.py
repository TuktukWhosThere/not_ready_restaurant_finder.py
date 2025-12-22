# app/schemas/visit.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserVisitBase(BaseModel):
    user_id: int
    restaurant_id: int
    visited: Optional[bool] = False
    forbidden: Optional[bool] = False
    rating_given: Optional[float] = None

class UserVisitCreate(UserVisitBase):
    """Schema for creating a new visit or forbid entry"""
    pass

class UserVisitUpdate(BaseModel):
    """Schema for updating a visit record"""
    visited: Optional[bool] = None
    forbidden: Optional[bool] = None
    rating_given: Optional[float] = None

class UserVisitRead(UserVisitBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Important for SQLAlchemy models
