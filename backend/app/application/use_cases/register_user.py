"""
User Registration Use Case.
Handles new user registration workflow.
"""

import logging
from typing import Optional

from ..dto.auth_request import RegisterRequest
from ..dto.auth_response import RegisterResponse, UserResponse, AuthTokens
from ...domain.entities.user import User
from ...domain.interfaces.user_repository import IUserRepository
from ...domain.interfaces.auth_service import IAuthService
from ...domain.exceptions import ValidationException, EntityExistsException

logger = logging.getLogger(__name__)


class RegisterUserUseCase:
    """
    Use case for user registration.

    This use case handles:
    - Validation of registration data
    - Checking for existing users
    - Creating new user account
    - Generating authentication tokens
    - Sending verification email (future)
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        auth_service: IAuthService
    ):
        """
        Initialize registration use case.

        Args:
            user_repository: Repository for user persistence
            auth_service: Service for authentication operations
        """
        self._user_repository = user_repository
        self._auth_service = auth_service

    async def execute(self, request: RegisterRequest) -> RegisterResponse:
        """
        Execute user registration.

        Args:
            request: Registration request data

        Returns:
            Registration response with user data and tokens

        Raises:
            ValidationException: If validation fails
            EntityExistsException: If user already exists
        """
        logger.info(f"Registering new user: {request.email}")

        # Validate request
        errors = request.validate()
        if errors:
            raise ValidationException("Invalid registration data", {"errors": errors})

        # Check if user already exists
        existing_user = await self._user_repository.get_user_by_email(request.email)
        if existing_user:
            raise EntityExistsException("User", request.email)

        # Create new user entity
        user = User(
            email=request.email.lower(),
            name=request.name.strip()
        )

        # Set password (this hashes the password)
        user.set_password(request.password)

        # Save user to repository
        created_user = await self._user_repository.create_user(user)

        # Generate authentication tokens
        auth_result = await self._auth_service.register_user(
            email=created_user.email,
            password=request.password,  # Auth service will verify against hash
            name=created_user.name
        )

        # Create response DTOs
        user_response = UserResponse.from_user_entity(created_user)
        tokens = AuthTokens(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            expires_in=auth_result.get("expires_in", 3600)
        )

        # TODO: Send verification email
        # await self._email_service.send_verification_email(created_user.email, verification_token)

        logger.info(f"User registered successfully: {created_user.id}")

        return RegisterResponse(
            user=user_response,
            tokens=tokens
        )