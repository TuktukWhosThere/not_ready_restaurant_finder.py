# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    place_id = Column(String, unique=True)
    vicinity = Column(String)
    rating = Column(Float)
    user_ratings = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp for data freshness


class ApiCall(Base):
    __tablename__ = "api_calls"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Integer)
    result_count = Column(Integer)
    place_type = Column(String)  # "restaurant"
    created_at = Column(DateTime, default=datetime.utcnow)


class UserVisit(Base):
    __tablename__ = "user_visits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    visited = Column(Boolean, default=False)
    forbidden = Column(Boolean, default=False)
    rating_given = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="visits")
    restaurant = relationship("Restaurant", backref="visits")

