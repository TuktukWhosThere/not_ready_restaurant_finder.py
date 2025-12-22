# app/routes/auth_routes.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.auth import create_user, get_user_by_email, verify_user_password

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["Auth"])

# ---------------- Register ----------------
@router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = create_user(db, username, email, password)
    if not user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Username or email already exists"},
            status_code=400
        )
    # Optionally log the user in immediately
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)

# ---------------- Login ----------------
@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email)
    if not user or not verify_user_password(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"},
            status_code=400
        )
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)

# ---------------- Logout ----------------
@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
