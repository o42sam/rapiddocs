"""
User Entity.
Represents a user of the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
import hashlib
import secrets
import bcrypt


@dataclass
class User:
    """
    User entity.

    Attributes:
        email: User's email address
        name: User's full name
        id: Unique identifier
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        is_active: Whether the user account is active
        credits: Number of generation credits
        subscription_tier: Subscription level (free, pro, enterprise)
        preferences: User preferences dictionary
    """
    email: str
    name: str
    password_hash: str = ""  # Will be set via set_password method
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_verified: bool = False  # Email verification status
    credits: int = 10  # Default free tier credits
    subscription_tier: str = "free"
    preferences: Dict[str, Any] = field(default_factory=dict)
    refresh_token: Optional[str] = None  # Current refresh token

    def has_credits(self) -> bool:
        """Check if user has credits available."""
        return self.credits > 0

    def use_credit(self) -> bool:
        """
        Use one credit.

        Returns:
            True if credit was used, False if no credits available
        """
        if self.credits > 0:
            self.credits -= 1
            self.updated_at = datetime.utcnow()
            return True
        return False

    def add_credits(self, amount: int) -> None:
        """
        Add credits to user account.

        Args:
            amount: Number of credits to add
        """
        if amount > 0:
            self.credits += amount
            self.updated_at = datetime.utcnow()

    def update_subscription(self, tier: str, credits: int) -> None:
        """
        Update user subscription.

        Args:
            tier: New subscription tier
            credits: New credit amount
        """
        self.subscription_tier = tier
        self.credits = credits
        self.updated_at = datetime.utcnow()

    def set_preference(self, key: str, value: Any) -> None:
        """
        Set a user preference.

        Args:
            key: Preference key
            value: Preference value
        """
        self.preferences[key] = value
        self.updated_at = datetime.utcnow()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference.

        Args:
            key: Preference key
            default: Default value if key not found

        Returns:
            Preference value or default
        """
        return self.preferences.get(key, default)

    def set_password(self, password: str) -> None:
        """
        Hash and set user password using bcrypt (for compatibility with existing DB).

        Args:
            password: Plain text password
        """
        # Use bcrypt to match existing database format
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            salt
        ).decode('utf-8')
        self.updated_at = datetime.utcnow()

    def verify_password(self, password: str) -> bool:
        """
        Verify password against hash.
        Supports both bcrypt (existing users) and PBKDF2 (legacy) formats.

        Args:
            password: Plain text password to verify

        Returns:
            True if password matches
        """
        if not self.password_hash:
            return False

        try:
            # First try bcrypt (existing database format)
            if self.password_hash.startswith('$2'):  # bcrypt hashes start with $2
                return bcrypt.checkpw(
                    password.encode('utf-8'),
                    self.password_hash.encode('utf-8')
                )

            # Fall back to PBKDF2 format (colon-separated)
            elif ':' in self.password_hash:
                stored_hash, salt = self.password_hash.split(':')
                password_hash = hashlib.pbkdf2_hmac(
                    'sha256',
                    password.encode('utf-8'),
                    salt.encode('utf-8'),
                    100000
                ).hex()
                return password_hash == stored_hash

            # Unknown format
            return False

        except Exception as e:
            # Log the error for debugging
            print(f"Password verification error: {e}")
            return False

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert to dictionary representation.

        Args:
            include_sensitive: Whether to include sensitive data

        Returns:
            Dictionary representation
        """
        data = {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "credits": self.credits,
            "subscription_tier": self.subscription_tier,
            "preferences": self.preferences
        }

        if include_sensitive:
            data["password_hash"] = self.password_hash
            data["refresh_token"] = self.refresh_token

        return data