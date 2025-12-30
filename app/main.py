# app/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from app.database import create_tables, get_db
from app.routes.user_routes import router as user_router
from app.routes.restaurant_routes import router as restaurant_router
from app.routes.user_choices import router as user_choices_router
from app.routes.auth_routes import router as auth_router
import os
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware


load_dotenv()  # load env vars from .env
SESSION_SECRET = os.getenv("SESSION_SECRET")

# 1️⃣ Create the FastAPI app first
app = FastAPI(
    title="Restaurant Download API",
    description="API to manage users and fetch restaurant data",
    version="1.0.0"
)

# 2️⃣ Add session middleware AFTER app is created
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# 3️⃣ Set up templates directory
templates = Jinja2Templates(directory="app/templates")

# 4️⃣ Optional: serve static JS/CSS files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 5️⃣ Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    print("✅ Database tables created")

# 6️⃣ Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(restaurant_router, prefix="/restaurants", tags=["Restaurants"])
app.include_router(user_choices_router, prefix="/user_choices", tags=["User Choices"])

# 7️⃣ Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# 8️⃣ Serve frontend UI
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 9️⃣ Show suggestion page
@app.get("/suggestion")
def show_suggestion(
    request: Request,
    user_id: int,
    latitude: float,
    longitude: float,
    radius: int,
    strategy: str = "random",
    db: Session = Depends(get_db)
):
    from app.api import suggest_restaurant
    restaurant = suggest_restaurant(user_id, latitude, longitude, radius, strategy, db)
    return templates.TemplateResponse(
        "suggestion.html",
        {
            "request": request,
            "restaurant": restaurant,
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            "strategy": strategy
        }
    )
