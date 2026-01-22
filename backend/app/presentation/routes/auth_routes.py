"""
Authentication API Routes.
Handles user registration, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from ..schemas.auth_schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    AuthResponse,
    TokenResponse,
    UserResponse,
    MessageResponse,
    ErrorResponse
)
from ...application.dto.auth_request import (
    RegisterRequest as RegisterDTO,
    LoginRequest as LoginDTO
)
from ...application.use_cases.register_user import RegisterUserUseCase
from ...application.use_cases.login_user import LoginUserUseCase
from ...domain.interfaces.auth_service import IAuthService
from ...domain.exceptions import (
    ValidationException,
    EntityExistsException,
    AuthenticationException,
    TokenException
)

router = APIRouter()
security = HTTPBearer()


def get_auth_service() -> IAuthService:
    """Dependency to get auth service - will be injected from main.py"""
    # This will be replaced with actual injection
    raise NotImplementedError("Auth service not configured")


def get_register_use_case() -> RegisterUserUseCase:
    """Dependency to get register use case - will be injected from main.py"""
    # This will be replaced with actual injection
    raise NotImplementedError("Register use case not configured")


def get_login_use_case() -> LoginUserUseCase:
    """Dependency to get login use case - will be injected from main.py"""
    # This will be replaced with actual injection
    raise NotImplementedError("Login use case not configured")


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "User already exists"}
    }
)
async def register(
    request: RegisterRequest,
    register_use_case: RegisterUserUseCase = Depends(get_register_use_case)
):
    """
    Register a new user account.

    This endpoint:
    - Validates registration data
    - Creates new user account
    - Generates authentication tokens
    - Returns user data and tokens
    """
    try:
        # Convert to DTO
        register_dto = RegisterDTO(
            email=request.email,
            password=request.password,
            name=request.name
        )

        # Execute use case
        result = await register_use_case.execute(register_dto)

        # Convert to response schema
        return AuthResponse(
            user=UserResponse(
                id=result.user.id,
                email=result.user.email,
                name=result.user.name,
                is_active=result.user.is_active,
                is_verified=result.user.is_verified,
                credits=result.user.credits,
                subscription_tier=result.user.subscription_tier,
                created_at=result.user.created_at,
                last_login=result.user.last_login
            ),
            tokens=TokenResponse(
                access_token=result.tokens.access_token,
                refresh_token=result.tokens.refresh_token,
                token_type=result.tokens.token_type,
                expires_in=result.tokens.expires_in
            )
        )

    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
            headers={"X-Error-Type": "validation"}
        )
    except EntityExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
            headers={"X-Error-Type": "conflict"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Authentication failed"}
    }
)
async def login(
    request: LoginRequest,
    login_use_case: LoginUserUseCase = Depends(get_login_use_case)
):
    """
    Login with email and password.

    This endpoint:
    - Validates credentials
    - Authenticates user
    - Generates authentication tokens
    - Returns user data and tokens
    """
    try:
        # Convert to DTO
        login_dto = LoginDTO(
            email=request.email,
            password=request.password
        )

        # Execute use case
        result = await login_use_case.execute(login_dto)

        # Convert to response schema
        return AuthResponse(
            user=UserResponse(
                id=result.user.id,
                email=result.user.email,
                name=result.user.name,
                is_active=result.user.is_active,
                is_verified=result.user.is_verified,
                credits=result.user.credits,
                subscription_tier=result.user.subscription_tier,
                created_at=result.user.created_at,
                last_login=result.user.last_login
            ),
            tokens=TokenResponse(
                access_token=result.tokens.access_token,
                refresh_token=result.tokens.refresh_token,
                token_type=result.tokens.token_type,
                expires_in=result.tokens.expires_in
            )
        )

    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token"}
    }
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: IAuthService = Depends(get_auth_service)
):
    """
    Refresh authentication tokens.

    This endpoint:
    - Validates refresh token
    - Generates new access and refresh tokens
    - Returns new tokens
    """
    try:
        result = await auth_service.refresh_token(request.refresh_token)

        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type="Bearer",
            expires_in=result.get("expires_in", 3600)
        )

    except TokenException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: IAuthService = Depends(get_auth_service)
):
    """
    Logout current user.

    This endpoint:
    - Validates current token
    - Invalidates refresh token
    - Returns success message
    """
    try:
        token = credentials.credentials
        success = await auth_service.logout(token)

        if success:
            return MessageResponse(message="Logged out successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: IAuthService = Depends(get_auth_service)
):
    """
    Get current authenticated user.

    This endpoint:
    - Validates access token
    - Returns current user data
    """
    try:
        token = credentials.credentials
        user_data = await auth_service.get_current_user(token)

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return UserResponse(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            is_active=user_data["is_active"],
            is_verified=user_data["is_verified"],
            credits=user_data["credits"],
            subscription_tier=user_data["subscription_tier"],
            created_at=user_data["created_at"],
            last_login=user_data.get("last_login")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user data"
        )