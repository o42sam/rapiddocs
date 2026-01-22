"""
User Login Use Case.
Handles user authentication workflow.
"""

import logging
from typing import Optional

from ..dto.auth_request import LoginRequest
from ..dto.auth_response import LoginResponse, UserResponse, AuthTokens
from ...domain.interfaces.user_repository import IUserRepository
from ...domain.interfaces.auth_service import IAuthService
from ...domain.exceptions import ValidationException, AuthenticationException

logger = logging.getLogger(__name__)


class LoginUserUseCase:
    """
    Use case for user login.

    This use case handles:
    - Validation of login credentials
    - User authentication
    - Token generation
    - Updating last login timestamp
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        auth_service: IAuthService
    ):
        """
        Initialize login use case.

        Args:
            user_repository: Repository for user operations
            auth_service: Service for authentication
        """
        self._user_repository = user_repository
        self._auth_service = auth_service

    async def execute(self, request: LoginRequest) -> LoginResponse:
        """
        Execute user login.

        Args:
            request: Login request data

        Returns:
            Login response with user data and tokens

        Raises:
            ValidationException: If validation fails
            AuthenticationException: If authentication fails
        """
        logger.info(f"User login attempt: {request.email}")

        # Validate request
        errors = request.validate()
        if errors:
            raise ValidationException("Invalid login data", {"errors": errors})

        # Get user by email
        user = await self._user_repository.get_user_by_email(request.email.lower())
        if not user:
            raise AuthenticationException("Invalid email or password")

        # Verify password
        if not user.verify_password(request.password):
            raise AuthenticationException("Invalid email or password")

        # Check if account is active
        if not user.is_active:
            raise AuthenticationException("Account is disabled. Please contact support.")

        # Generate authentication tokens
        auth_result = await self._auth_service.login(
            email=user.email,
            password=request.password
        )

        # Update last login
        await self._user_repository.update_last_login(user.id)
        user.update_last_login()

        # Create response DTOs
        user_response = UserResponse.from_user_entity(user)
        tokens = AuthTokens(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            expires_in=auth_result.get("expires_in", 3600)
        )

        logger.info(f"User logged in successfully: {user.id}")

        return LoginResponse(
            user=user_response,
            tokens=tokens
        )