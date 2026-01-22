"""
Authentication Response DTOs.
Response data transfer objects for authentication.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class AuthTokens:
    """
    DTO for authentication tokens.

    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token
        token_type: Token type (Bearer)
        expires_in: Token expiration time in seconds
    """
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600  # 1 hour

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in
        }


@dataclass
class UserResponse:
    """
    DTO for user data in responses.

    Attributes:
        id: User's unique identifier
        email: User's email address
        name: User's full name
        is_active: Whether account is active
        is_verified: Whether email is verified
        credits: Available credits
        subscription_tier: Subscription level
        created_at: Account creation timestamp
    """
    id: str
    email: str
    name: str
    is_active: bool
    is_verified: bool
    credits: int
    subscription_tier: str
    created_at: datetime
    last_login: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "credits": self.credits,
            "subscription_tier": self.subscription_tier,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

    @classmethod
    def from_user_entity(cls, user: Any) -> "UserResponse":
        """
        Create from User entity.

        Args:
            user: User entity

        Returns:
            UserResponse DTO
        """
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            credits=user.credits,
            subscription_tier=user.subscription_tier,
            created_at=user.created_at,
            last_login=user.last_login
        )


@dataclass
class LoginResponse:
    """
    DTO for login response.

    Attributes:
        user: User data
        tokens: Authentication tokens
    """
    user: UserResponse
    tokens: AuthTokens

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user": self.user.to_dict(),
            "tokens": self.tokens.to_dict()
        }


@dataclass
class RegisterResponse:
    """
    DTO for registration response.

    Attributes:
        user: Created user data
        tokens: Authentication tokens
        message: Success message
    """
    user: UserResponse
    tokens: AuthTokens
    message: str = "Registration successful. Please verify your email."

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user": self.user.to_dict(),
            "tokens": self.tokens.to_dict(),
            "message": self.message
        }