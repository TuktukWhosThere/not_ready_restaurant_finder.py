# app.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import init_db, SessionLocal
from api import fetch_restaurants
from auth import create_user

app = FastAPI()

# Initialize the database
init_db()

# Dependency for getting the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register_user(email: str, password: str, db: Session = Depends(get_db)):
    user = create_user(db, email, password)
    if not user:
        raise HTTPException(status_code=400, detail="User already exists.")
    return {"message": "User created successfully"}

@app.get("/fetch-restaurants")
def fetch_data(db: Session = Depends(get_db)):
    fetch_restaurants(db, latitude=50.0731173, longitude=14.4385034)
    return {"message": "Restaurants fetched successfully"}
