from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    UserResponse,
    AuthResponse,
    PasswordChangeRequest
)
from app.models.user import User
from app.utils.security import (
    hash_password,
    verify_password,
    create_tokens,
    decode_refresh_token
)
from app.utils.dependencies import get_current_user, get_current_active_user
from app.database import get_database
from bson import ObjectId

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest):
    """
    Register a new user

    Args:
        user_data: User registration data

    Returns:
        AuthResponse with user data and tokens

    Raises:
        HTTPException: If email or username already exists
    """
    db = get_database()

    # Check if email already exists
    existing_user = await db.users.find_one({"email": user_data.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_username = await db.users.find_one({"username": user_data.username.lower()})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user document
    user = User(
        email=user_data.email.lower(),
        username=user_data.username.lower(),
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Insert into database
    result = await db.users.insert_one(user.model_dump(by_alias=True, exclude={"id"}))
    user.id = result.inserted_id

    # Create tokens
    tokens = create_tokens(str(user.id), user.email)

    # Create response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        credits=user.credits,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at.isoformat()
    )

    token_response = TokenResponse(**tokens)

    return AuthResponse(user=user_response, tokens=token_response)


@router.post("/login", response_model=AuthResponse)
async def login_user(login_data: UserLoginRequest):
    """
    Login user and return tokens

    Args:
        login_data: User login credentials

    Returns:
        AuthResponse with user data and tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    db = get_database()

    # Find user by email
    user_data = await db.users.find_one({"email": login_data.email.lower()})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    user = User(**user_data)

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Update last login
    await db.users.update_one(
        {"_id": user.id},
        {"$set": {"last_login": datetime.utcnow()}}
    )

    # Create tokens
    tokens = create_tokens(str(user.id), user.email)

    # Create response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        credits=user.credits,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at.isoformat()
    )

    token_response = TokenResponse(**tokens)

    return AuthResponse(user=user_response, tokens=token_response)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: TokenRefreshRequest):
    """
    Refresh access token using refresh token

    Args:
        refresh_data: Refresh token

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Decode refresh token
    payload = decode_refresh_token(refresh_data.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Extract user data
    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Verify user exists and is active
    db = get_database()
    user_data = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    user = User(**user_data)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create new tokens
    tokens = create_tokens(user_id, email)

    return TokenResponse(**tokens)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        credits=current_user.credits,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat()
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Change user password

    Args:
        password_data: Current and new password
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: If current password is incorrect
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Hash new password
    new_hashed_password = hash_password(password_data.new_password)

    # Update password in database
    db = get_database()
    await db.users.update_one(
        {"_id": current_user.id},
        {
            "$set": {
                "hashed_password": new_hashed_password,
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """
    Logout user (client should delete tokens)

    Note: Since we're using JWT, actual logout is handled client-side by deleting tokens.
    This endpoint is mainly for logging purposes or future blacklist implementation.

    Args:
        current_user: Current authenticated user

    Returns:
        Success message
    """
    # In a production system, you might want to:
    # 1. Add the token to a blacklist (stored in Redis)
    # 2. Log the logout event
    # 3. Clear any session data

    return {"message": "Logged out successfully"}
