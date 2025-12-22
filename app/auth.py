# app/auth.py
from sqlalchemy.orm import Session
from app import models
from app.security import hash_password, verify_password


def create_user(db: Session, username: str, email: str, password: str):
    existing_user = (
        db.query(models.User)
        .filter(
            (models.User.username == username)
            | (models.User.email == email)
        )
        .first()
    )
    if existing_user:
        return None

    user = models.User(
        username=username,
        email=email,
        password=hash_password(password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_user_password(plain_password: str, hashed_password: str):
    return verify_password(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user

