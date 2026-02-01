"""User authentication routes for frontend users."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt
from bson import ObjectId
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models for requests/responses
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class User(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    credits: int = 0
    is_active: bool = True
    is_verified: bool = False
    created_at: str

class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class AuthResponse(BaseModel):
    user: User
    tokens: AuthTokens

class RefreshTokenRequest(BaseModel):
    refresh_token: str

router = APIRouter(prefix="/auth", tags=["User Auth"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=AuthResponse)
async def login(request: Request, credentials: UserLogin):
    """User login endpoint."""
    db = request.app.state.db

    # Find user by email
    user = await db.users.find_one({"email": credentials.email})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check password - try multiple field names for compatibility
    password_field = user.get("password") or user.get("hashedPassword") or user.get("hashed_password")

    if not password_field:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(credentials.password, password_field):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Update last login
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )

    # Create tokens
    token_data = {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "username": user.get("username", user["email"])
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Get user credits
    credits = user.get("credits", 0)

    # Prepare response
    user_response = User(
        id=str(user["_id"]),
        email=user["email"],
        username=user.get("username", user["email"]),
        full_name=user.get("full_name") or user.get("fullName") or user.get("displayName", ""),
        credits=credits,
        is_active=user.get("is_active", True),
        is_verified=user.get("emailVerified", False),
        created_at=str(user.get("created_at", user.get("createdAt", datetime.utcnow())))
    )

    tokens = AuthTokens(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600
    )

    return AuthResponse(user=user_response, tokens=tokens)

@router.post("/register", response_model=AuthResponse)
async def register(request: Request, registration: UserRegister):
    """User registration endpoint."""
    db = request.app.state.db

    # Check if user already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"email": registration.email},
            {"username": registration.username}
        ]
    })

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )

    # Hash password
    hashed_password = get_password_hash(registration.password)

    # Create user document
    user_data = {
        "_id": ObjectId(),
        "email": registration.email,
        "username": registration.username,
        "password": hashed_password,
        "hashedPassword": hashed_password,  # Alternative field name
        "full_name": registration.full_name or registration.username,
        "displayName": registration.full_name or registration.username,
        "credits": 10,  # Initial credits for new users
        "is_active": True,
        "emailVerified": False,
        "created_at": datetime.utcnow(),
        "createdAt": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "provider": "email",
        "role": "user"
    }

    # Insert user
    result = await db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id

    # Create initial credits entry
    await db.credits.insert_one({
        "_id": ObjectId(),
        "user_email": registration.email,
        "user_id": str(result.inserted_id),
        "total_credits": 10,
        "used_credits": 0,
        "remaining_credits": 10,
        "credit_history": [{
            "action": "initial_grant",
            "amount": 10,
            "timestamp": datetime.utcnow(),
            "description": "Welcome bonus"
        }],
        "created_at": datetime.utcnow()
    })

    # Create tokens
    token_data = {
        "user_id": str(result.inserted_id),
        "email": registration.email,
        "username": registration.username
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Prepare response
    user_response = User(
        id=str(result.inserted_id),
        email=registration.email,
        username=registration.username,
        full_name=registration.full_name or registration.username,
        credits=10,
        is_active=True,
        is_verified=False,
        created_at=str(datetime.utcnow())
    )

    tokens = AuthTokens(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600
    )

    return AuthResponse(user=user_response, tokens=tokens)

@router.get("/me", response_model=User)
async def get_current_user(request: Request):
    """Get current user information from database based on JWT token."""
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = auth_header.replace("Bearer ", "")

    try:
        # Decode the access token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Fetch user from database
    db = request.app.state.db

    # Try to find by ObjectId first
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except:
        user = None

    # If not found, try by id field
    if not user:
        user = await db.users.find_one({"id": user_id})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Return real user data from database
    return User(
        id=str(user["_id"]),
        email=user["email"],
        username=user.get("username", user["email"]),
        full_name=user.get("full_name") or user.get("fullName") or user.get("displayName", ""),
        credits=user.get("credits", 0),
        is_active=user.get("is_active", True),
        is_verified=user.get("emailVerified", False),
        created_at=str(user.get("created_at", user.get("createdAt", datetime.utcnow())))
    )

@router.post("/logout")
async def logout(request: Request):
    """User logout endpoint."""
    # In a real implementation, you might invalidate the token here
    return {"message": "Logged out successfully"}

@router.post("/refresh", response_model=AuthTokens)
async def refresh_token(request: Request, body: RefreshTokenRequest):
    """Refresh access token."""
    try:
        # Decode refresh token
        payload = jwt.decode(
            body.refresh_token,
            settings.JWT_REFRESH_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # Create new tokens
        token_data = {
            "user_id": payload["user_id"],
            "email": payload["email"],
            "username": payload["username"]
        }

        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        return AuthTokens(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=3600
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )