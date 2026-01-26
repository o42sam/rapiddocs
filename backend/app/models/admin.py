"""Admin user models for authentication and authorization."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class AdminUser(BaseModel):
    """Admin user model for database storage."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    full_name: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    created_by_referral: Optional[str] = None  # Referral key used for registration
    permissions: List[str] = []  # List of permission strings

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "username": "admin",
                "email": "admin@rapiddocs.io",
                "full_name": "Admin User",
                "is_active": True,
                "is_superuser": True,
                "permissions": ["users:read", "users:write", "docs:admin"]
            }
        }


class ReferralKey(BaseModel):
    """Referral key for admin registration."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    key: str = Field(..., min_length=32, max_length=64)
    created_by: str  # Admin username who created this key
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = None
    used_by: Optional[str] = None  # Username of admin who used this key
    is_active: bool = True
    max_uses: int = 1
    current_uses: int = 0
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AdminSession(BaseModel):
    """Admin session tracking for monitoring."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    admin_id: str
    username: str
    ip_address: str
    user_agent: str
    login_time: datetime = Field(default_factory=datetime.utcnow)
    logout_time: Optional[datetime] = None
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}