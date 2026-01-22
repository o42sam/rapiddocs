"""
Authentication Request DTOs.
Data transfer objects for authentication requests.
"""

from dataclasses import dataclass
from typing import Optional, List
import re


@dataclass
class RegisterRequest:
    """
    DTO for user registration request.

    Attributes:
        email: User's email address
        password: User's password
        name: User's full name
    """
    email: str
    password: str
    name: str

    def validate(self) -> List[str]:
        """
        Validate registration data.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate email
        if not self.email:
            errors.append("Email is required")
        elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.email):
            errors.append("Invalid email format")

        # Validate password
        if not self.password:
            errors.append("Password is required")
        elif len(self.password) < 8:
            errors.append("Password must be at least 8 characters")
        elif not re.search(r"[A-Z]", self.password):
            errors.append("Password must contain at least one uppercase letter")
        elif not re.search(r"[a-z]", self.password):
            errors.append("Password must contain at least one lowercase letter")
        elif not re.search(r"[0-9]", self.password):
            errors.append("Password must contain at least one number")

        # Validate name
        if not self.name:
            errors.append("Name is required")
        elif len(self.name.strip()) < 2:
            errors.append("Name must be at least 2 characters")

        return errors


@dataclass
class LoginRequest:
    """
    DTO for login request.

    Attributes:
        email: User's email address
        password: User's password
    """
    email: str
    password: str

    def validate(self) -> List[str]:
        """
        Validate login data.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.email:
            errors.append("Email is required")
        if not self.password:
            errors.append("Password is required")

        return errors


@dataclass
class RefreshTokenRequest:
    """
    DTO for refresh token request.

    Attributes:
        refresh_token: Valid refresh token
    """
    refresh_token: str

    def validate(self) -> List[str]:
        """
        Validate refresh token.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.refresh_token:
            errors.append("Refresh token is required")

        return errors


@dataclass
class ResetPasswordRequest:
    """
    DTO for password reset request.

    Attributes:
        email: User's email address
    """
    email: str

    def validate(self) -> List[str]:
        """
        Validate reset password data.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.email:
            errors.append("Email is required")
        elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.email):
            errors.append("Invalid email format")

        return errors


@dataclass
class ChangePasswordRequest:
    """
    DTO for password change request.

    Attributes:
        old_password: Current password
        new_password: New password
    """
    old_password: str
    new_password: str

    def validate(self) -> List[str]:
        """
        Validate password change data.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.old_password:
            errors.append("Current password is required")

        if not self.new_password:
            errors.append("New password is required")
        elif len(self.new_password) < 8:
            errors.append("New password must be at least 8 characters")
        elif not re.search(r"[A-Z]", self.new_password):
            errors.append("New password must contain at least one uppercase letter")
        elif not re.search(r"[a-z]", self.new_password):
            errors.append("New password must contain at least one lowercase letter")
        elif not re.search(r"[0-9]", self.new_password):
            errors.append("New password must contain at least one number")
        elif self.old_password == self.new_password:
            errors.append("New password must be different from current password")

        return errors