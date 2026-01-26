"""Authentication schemas for API requests and responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class AdminLogin(BaseModel):
    """Admin login request schema."""
    username: str
    password: str


class AdminRegister(BaseModel):
    """Admin registration request schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    referral_key: str = Field(..., min_length=32)

    @validator('password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None
    admin_id: Optional[str] = None
    permissions: list = []


class AdminResponse(BaseModel):
    """Admin user response schema."""
    id: str
    username: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime]
    permissions: list


class ReferralKeyCreate(BaseModel):
    """Create referral key request schema."""
    max_uses: int = Field(default=1, ge=1, le=10)
    expires_in_days: Optional[int] = Field(None, ge=1, le=30)
    notes: Optional[str] = Field(None, max_length=200)


class ReferralKeyResponse(BaseModel):
    """Referral key response schema."""
    key: str
    created_by: str
    created_at: datetime
    is_active: bool
    max_uses: int
    current_uses: int
    expires_at: Optional[datetime]
    notes: Optional[str]


class DashboardStats(BaseModel):
    """Dashboard statistics response schema."""
    total_users: int
    daily_active_users: int
    weekly_active_users: int
    monthly_active_users: int
    total_documents_generated: int
    documents_today: int
    documents_this_week: int
    documents_this_month: int
    total_admins: int
    active_admins: int
    server_uptime: str
    last_deployment: datetime