from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, Field, EmailStr, BeforeValidator, PlainSerializer
from bson import ObjectId


def validate_object_id(v):
    """Validate and convert to ObjectId"""
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


# Pydantic v2 compatible ObjectId type
PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str)
]


class User(BaseModel):
    """User model for database storage"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: str  # Using string for database storage
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    credits: int = 40  # Default 40 free credits for new users
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "is_active": True,
                "is_verified": False
            }
        }


class UserInDB(User):
    """User model with hashed password for internal use"""
    pass
