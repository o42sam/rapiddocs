"""
JWT Authentication Service Implementation.
Handles JWT token generation and validation.
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from ...domain.interfaces.auth_service import IAuthService
from ...domain.interfaces.user_repository import IUserRepository
from ...domain.exceptions import AuthenticationException, TokenException
from ...domain.entities.user import User

logger = logging.getLogger(__name__)


class JWTAuthService(IAuthService):
    """
    JWT-based authentication service implementation.

    This service handles:
    - JWT token generation (access and refresh)
    - Token validation and decoding
    - User authentication
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 7
    ):
        """
        Initialize JWT authentication service.

        Args:
            user_repository: Repository for user operations
            secret_key: Secret key for JWT signing
            algorithm: JWT algorithm (default: HS256)
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
        """
        self._user_repository = user_repository
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    async def register_user(
        self,
        email: str,
        password: str,
        name: str
    ) -> Dict[str, Any]:
        """
        Register a new user and generate tokens.

        Args:
            email: User's email
            password: User's password (already validated)
            name: User's name

        Returns:
            Dictionary with tokens and user data
        """
        # User is already created in the use case
        # Just generate tokens for the new user
        user = await self._user_repository.get_user_by_email(email)
        if not user:
            raise AuthenticationException("User registration failed")

        # Generate tokens
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)

        # Store refresh token
        user.refresh_token = refresh_token
        await self._user_repository.update_user(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": self._access_token_expire_minutes * 60,
            "user_id": user.id
        }

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
            Dictionary with tokens
        """
        user = await self._user_repository.get_user_by_email(email)
        if not user or not user.verify_password(password):
            raise AuthenticationException("Invalid credentials")

        if not user.is_active:
            raise AuthenticationException("Account is disabled")

        # Generate tokens
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)

        # Store refresh token
        user.refresh_token = refresh_token
        await self._user_repository.update_user(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": self._access_token_expire_minutes * 60,
            "user_id": user.id
        }

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
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None

    async def refresh_token(
        self,
        refresh_token: str
    ) -> Dict[str, Any]:
        """
        Generate new access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New tokens
        """
        # Verify refresh token
        payload = await self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise TokenException("Invalid refresh token")

        # Get user
        user_id = payload.get("user_id")
        user = await self._user_repository.get_user_by_id(user_id)
        if not user or user.refresh_token != refresh_token:
            raise TokenException("Invalid refresh token")

        # Generate new tokens
        new_access_token = self._generate_access_token(user)
        new_refresh_token = self._generate_refresh_token(user)

        # Update stored refresh token
        user.refresh_token = new_refresh_token
        await self._user_repository.update_user(user)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "expires_in": self._access_token_expire_minutes * 60
        }

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
        payload = await self.verify_token(token)
        if not payload or payload.get("type") != "access":
            return None

        user_id = payload.get("user_id")
        user = await self._user_repository.get_user_by_id(user_id)
        if not user:
            return None

        return user.to_dict()

    async def logout(
        self,
        token: str
    ) -> bool:
        """
        Logout user (invalidate refresh token).

        Args:
            token: JWT token

        Returns:
            True if successful
        """
        payload = await self.verify_token(token)
        if not payload:
            return False

        user_id = payload.get("user_id")
        user = await self._user_repository.get_user_by_id(user_id)
        if user:
            user.refresh_token = None
            await self._user_repository.update_user(user)
            return True

        return False

    def _generate_access_token(self, user: User) -> str:
        """Generate JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=self._access_token_expire_minutes)
        payload = {
            "user_id": user.id,
            "email": user.email,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def _generate_refresh_token(self, user: User) -> str:
        """Generate JWT refresh token."""
        expire = datetime.utcnow() + timedelta(days=self._refresh_token_expire_days)
        payload = {
            "user_id": user.id,
            "email": user.email,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)