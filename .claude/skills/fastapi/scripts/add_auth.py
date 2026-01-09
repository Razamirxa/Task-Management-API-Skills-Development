#!/usr/bin/env python3
"""
Add JWT Authentication to FastAPI Project

Adds authentication scaffolding including:
- User model
- JWT token generation and validation
- Password hashing
- Login/register endpoints
- Protected route examples

Usage:
    python add_auth.py [--output-dir DIR]

Examples:
    python add_auth.py
    python add_auth.py --output-dir ./my-project
"""

import argparse
import os
from pathlib import Path


AUTH_ROUTER_TEMPLATE = '''"""
Authentication routes for user registration and login.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from .database import get_db
from .models import User


# JWT Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # Change this!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["authentication"])


# Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Password hashing
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# JWT functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Routes
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""

    # Check if user already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login to get access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user
'''

USER_MODEL_TEMPLATE = '''"""
User model for authentication.

Add this to your models.py file.
"""
from sqlalchemy import Boolean, Column, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
'''

REQUIREMENTS_TEMPLATE = '''# Authentication dependencies
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
'''


def add_auth(output_dir: str):
    """Add authentication scaffolding to a FastAPI project."""

    output_path = Path(output_dir)

    if not output_path.exists():
        print(f"Error: Directory '{output_path}' does not exist")
        return

    # Create auth router file
    auth_file = output_path / "auth.py"
    print(f"Creating {auth_file}...")
    auth_file.write_text(AUTH_ROUTER_TEMPLATE, encoding='utf-8')

    # Create user model file (as reference)
    models_snippet = output_path / "user_model_snippet.py"
    print(f"Creating {models_snippet}...")
    models_snippet.write_text(USER_MODEL_TEMPLATE, encoding='utf-8')

    # Create requirements snippet
    req_snippet = output_path / "auth_requirements.txt"
    print(f"Creating {req_snippet}...")
    req_snippet.write_text(REQUIREMENTS_TEMPLATE, encoding='utf-8')

    print("\n✅ Authentication scaffolding added successfully!")
    print("\nNext steps:")
    print("  1. Install dependencies:")
    print("     pip install python-jose[cryptography] passlib[bcrypt] python-multipart")
    print("\n  2. Add User model to your models.py:")
    print("     (See user_model_snippet.py for the model code)")
    print("\n  3. Include the auth router in your main.py:")
    print("     from auth import router as auth_router")
    print("     app.include_router(auth_router)")
    print("\n  4. Change SECRET_KEY in auth.py to a secure random string")
    print("\n  5. Run migrations to create users table")
    print("\nTest the endpoints at http://127.0.0.1:8000/docs")


def main():
    parser = argparse.ArgumentParser(
        description="Add JWT authentication to FastAPI project"
    )

    parser.add_argument(
        "--output-dir",
        default=".",
        help="Project directory (default: current directory)"
    )

    args = parser.parse_args()
    add_auth(args.output_dir)


if __name__ == "__main__":
    main()
