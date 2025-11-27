from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserRegisterRequest(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "SecurePass123",
                "full_name": "John Doe"
            }
        }


class UserLoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh"""
    refresh_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class UserResponse(BaseModel):
    """Schema for user response (without password)"""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    credits: int
    is_active: bool
    is_verified: bool
    created_at: str
    oauth_provider: Optional[str] = None
    profile_picture: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "credits": 40,
                "is_active": True,
                "is_verified": False,
                "created_at": "2025-01-15T10:30:00Z",
                "oauth_provider": None,
                "profile_picture": None
            }
        }


class AuthResponse(BaseModel):
    """Schema for authentication response with user data and tokens"""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "507f1f77bcf86cd799439011",
                    "email": "user@example.com",
                    "username": "johndoe",
                    "full_name": "John Doe",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2025-01-15T10:30:00Z"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 3600
                }
            }
        }


class PasswordChangeRequest(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPass123",
                "new_password": "NewSecurePass123"
            }
        }


class TokenData(BaseModel):
    """Schema for token data (used internally)"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    token_type: Optional[str] = None  # "access" or "refresh"


class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth callback"""
    code: str
    state: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": "4/0AX4XfWhPn...",
                "state": "random_state_string"
            }
        }


class GoogleUserInfo(BaseModel):
    """Schema for Google user information"""
    id: str
    email: str
    verified_email: bool
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
