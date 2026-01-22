"""
Authentication Pydantic Schemas.
Request and response models for authentication API.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=2, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "name": "John Doe"
            }
        }


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        }


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    email: str
    name: str
    is_active: bool
    is_verified: bool
    credits: int
    subscription_tier: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "name": "John Doe",
                "is_active": True,
                "is_verified": False,
                "credits": 10,
                "subscription_tier": "free",
                "created_at": "2024-01-15T10:00:00",
                "last_login": "2024-01-15T10:00:00"
            }
        }


class AuthResponse(BaseModel):
    """Authentication response schema."""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "name": "John Doe",
                    "is_active": True,
                    "is_verified": False,
                    "credits": 10,
                    "subscription_tier": "free",
                    "created_at": "2024-01-15T10:00:00",
                    "last_login": None
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "Bearer",
                    "expires_in": 3600
                }
            }
        }


class MessageResponse(BaseModel):
    """Simple message response schema."""
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation successful"
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    errors: Optional[list] = None

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Validation error",
                "errors": ["Email is required", "Password is too short"]
            }
        }