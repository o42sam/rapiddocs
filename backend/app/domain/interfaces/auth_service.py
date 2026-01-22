"""
Authentication Service Interface.
Defines the contract for authentication operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime


class IAuthService(ABC):
    """
    Interface for authentication services.
    Handles user authentication, token generation, and validation.
    """

    @abstractmethod
    async def register_user(
        self,
        email: str,
        password: str,
        name: str
    ) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            email: User's email address
            password: User's password (plain text - will be hashed)
            name: User's full name

        Returns:
            Dictionary containing user data and tokens

        Raises:
            ValidationException: If email already exists or data is invalid
        """
        pass

    @abstractmethod
    async def login(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Authenticate user and generate tokens.

        Args:
            email: User's email
            password: User's password

        Returns:
            Dictionary containing access token, refresh token, and user data

        Raises:
            AuthenticationException: If credentials are invalid
        """
        pass

    @abstractmethod
    async def verify_token(
        self,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Decoded token payload or None if invalid
        """
        pass

    @abstractmethod
    async def refresh_token(
        self,
        refresh_token: str
    ) -> Dict[str, Any]:
        """
        Generate new access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token and refresh token

        Raises:
            AuthenticationException: If refresh token is invalid
        """
        pass

    @abstractmethod
    async def get_current_user(
        self,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get current user from token.

        Args:
            token: JWT access token

        Returns:
            User data or None if invalid
        """
        pass

    @abstractmethod
    async def logout(
        self,
        token: str
    ) -> bool:
        """
        Logout user (invalidate token).

        Args:
            token: JWT token to invalidate

        Returns:
            True if successful
        """
        pass