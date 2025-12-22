# app/security.py
from passlib.context import CryptContext

# Initialize bcrypt password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Truncate to 72 characters to satisfy bcrypt limitation.
    """
    truncated = password[:72]
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against the hashed password.
    Returns True if it matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
