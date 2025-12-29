"""
Authentication Endpoints
JWT-based authentication with login, register, and token refresh
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import timedelta
import structlog

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
    get_current_user
)
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()


# Request/Response models
class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=2, max_length=100)


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response (without sensitive data)"""
    id: str
    email: str
    name: str
    role: str


class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# In-memory user store (replace with database in production)
# This is for demonstration - use database models in production
USERS_DB = {
    "admin@example.com": {
        "id": "user-001",
        "email": "admin@example.com",
        "name": "Admin User",
        "password_hash": get_password_hash("admin123"),
        "role": "admin"
    },
    "demo@example.com": {
        "id": "user-002",
        "email": "demo@example.com",
        "name": "Demo User",
        "password_hash": get_password_hash("demo1234"),
        "role": "viewer"
    }
}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    """
    Register a new user account

    Returns user info on success
    """
    # Check if email already exists
    if user.email in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user_id = f"user-{len(USERS_DB) + 1:03d}"
    new_user = {
        "id": user_id,
        "email": user.email,
        "name": user.name,
        "password_hash": get_password_hash(user.password),
        "role": "viewer"  # Default role
    }

    USERS_DB[user.email] = new_user

    logger.info("New user registered", user_id=user_id, email=user.email)

    return UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        role="viewer"
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Authenticate user and return JWT tokens

    Returns access and refresh tokens
    """
    # Find user
    user = USERS_DB.get(credentials.email)

    if not user:
        logger.warning("Login attempt for unknown email", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        logger.warning("Invalid password attempt", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"]
    }

    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data=token_data)

    logger.info("User logged in", user_id=user["id"], email=user["email"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: TokenRefresh):
    """
    Refresh access token using refresh token

    Returns new access and refresh tokens
    """
    # Decode refresh token
    payload = decode_token(request.refresh_token)

    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    token_data = {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role")
    }

    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_refresh_token(data=token_data)

    logger.info("Token refreshed", user_id=payload.get("sub"))

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user info

    Requires valid JWT token
    """
    # Find user in database
    for email, user in USERS_DB.items():
        if user["id"] == current_user["user_id"]:
            return UserResponse(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                role=user["role"]
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """
    Change current user's password

    Requires valid JWT token and current password
    """
    # Find user
    user = None
    for email, u in USERS_DB.items():
        if u["id"] == current_user["user_id"]:
            user = u
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify current password
    if not verify_password(request.current_password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )

    # Update password
    user["password_hash"] = get_password_hash(request.new_password)

    logger.info("Password changed", user_id=user["id"])

    return {"message": "Password changed successfully"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user (invalidate token)

    Note: JWT tokens are stateless. For proper logout,
    implement token blacklist in Redis or database.
    """
    logger.info("User logged out", user_id=current_user["user_id"])

    # In production, add token to blacklist in Redis
    # redis.setex(f"blacklist:{token}", ttl, "1")

    return {"message": "Logged out successfully"}
