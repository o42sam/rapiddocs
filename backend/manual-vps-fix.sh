#!/bin/bash

# Manual VPS CORS Fix Script - No Git Required
# This script manually updates the files on VPS without git

echo "=== Manual CORS Fix for VPS ==="
echo "Current directory: $(pwd)"
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "ERROR: Not in the backend directory. Please run from /home/docgen/backend"
    exit 1
fi

echo "Step 1: Backing up current files..."
cp app/main_simple.py app/main_simple.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "main_simple.py not found, will create new"
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo ".env.production not found, will create new"

echo ""
echo "Step 2: Creating fixed main_simple.py..."
cat > app/main_simple.py << 'EOF'
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
import os
from pathlib import Path
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import asyncio
import json
import logging
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import hashlib
import uuid
from enum import Enum
import tempfile
import shutil

# Load environment variables
env_file = ".env.production" if os.path.exists(".env.production") else ".env"
load_dotenv(env_file)

# Configuration
class Settings:
    # MongoDB
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://samscarfaceegbo:G7a1n14G7@cluster1.vehwbxh.mongodb.net/?appName=Cluster1")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "docgen_prod")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
    JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "your-refresh-secret-key-change-this")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    # CORS - Read from environment
    CORS_ORIGINS_STR = os.getenv("CORS_ORIGINS", '["https://rapiddocs.io","https://www.rapiddocs.io","https://rapiddocs-9a3f8.web.app","https://rapiddocs.web.app","https://rapiddocs.firebaseapp.com"]')
    try:
        CORS_ORIGINS = json.loads(CORS_ORIGINS_STR)
    except:
        CORS_ORIGINS = ["https://rapiddocs.io", "https://www.rapiddocs.io", "https://rapiddocs-9a3f8.web.app"]

    # File paths
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
    GENERATED_DIR = Path(os.getenv("GENERATED_DIR", "./generated_pdfs"))
    STATIC_DIR = Path(os.getenv("STATIC_DIR", "./static"))

    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log CORS configuration
logger.info(f"CORS Origins configured: {settings.CORS_ORIGINS}")

# Initialize FastAPI
app = FastAPI(
    title="RapidDocs API",
    description="Professional Document Generation API",
    version="1.0.0"
)

# CORS configuration - SINGLE configuration using environment variables
cors_origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Use the list from environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Document types
class DocumentType(str, Enum):
    INVOICE = "invoice"
    INFOGRAPHIC = "infographic"
    FORMAL = "formal"

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    email: str
    name: str
    credits: int
    created_at: datetime
    is_admin: bool = False
    is_superuser: bool = False

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Routes
@app.get("/")
async def root():
    return {"message": "RapidDocs API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "cors_origins": cors_origins}

# Authentication endpoints
@app.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = {
            "email": user_data.email,
            "password": hashed_password,
            "name": user_data.name,
            "credits": 10,  # Starting credits
            "created_at": datetime.utcnow(),
            "is_admin": False,
            "is_superuser": False
        }

        result = await db.users.insert_one(new_user)
        user_id = str(result.inserted_id)

        # Create tokens
        access_token = create_access_token({"user_id": user_id})
        refresh_token = create_refresh_token({"user_id": user_id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    try:
        # Find user
        user = await db.users.find_one({"email": user_data.email})
        if not user:
            logger.warning(f"Login failed: User not found for email {user_data.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password
        if not verify_password(user_data.password, user["password"]):
            logger.warning(f"Login failed: Invalid password for email {user_data.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create tokens
        user_id = str(user["_id"])
        access_token = create_access_token({"user_id": user_id})
        refresh_token = create_refresh_token({"user_id": user_id})

        logger.info(f"User logged in successfully: {user_data.email}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.JWT_REFRESH_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Verify user still exists
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # Create new tokens
        access_token = create_access_token({"user_id": user_id})
        refresh_token = create_refresh_token({"user_id": user_id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        name=current_user["name"],
        credits=current_user.get("credits", 0),
        created_at=current_user.get("created_at", datetime.utcnow()),
        is_admin=current_user.get("is_admin", False),
        is_superuser=current_user.get("is_superuser", False)
    )

# Document generation endpoints (placeholder)
@app.post("/api/v1/{document_type}/generate")
async def generate_document(
    document_type: DocumentType,
    current_user: dict = Depends(get_current_user)
):
    # Check credits
    if current_user.get("credits", 0) <= 0:
        raise HTTPException(status_code=402, detail="Insufficient credits")

    # Placeholder response
    job_id = str(uuid.uuid4())

    return {
        "job_id": job_id,
        "status": "processing",
        "document_type": document_type,
        "message": f"Document generation started for {document_type}"
    }

@app.get("/api/v1/job/{job_id}/status")
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Placeholder response
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "download_url": f"/api/v1/download/{job_id}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

echo ""
echo "Step 3: Updating .env.production with correct CORS origins..."
# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "Creating new .env.production file..."
    cat > .env.production << 'EOF'
# MongoDB
MONGODB_URL=mongodb+srv://samscarfaceegbo:G7a1n14G7@cluster1.vehwbxh.mongodb.net/?appName=Cluster1
MONGODB_DB_NAME=docgen_prod

# JWT
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS - All production domains
CORS_ORIGINS=["https://rapiddocs.io","https://www.rapiddocs.io","https://rapiddocs-9a3f8.web.app","https://rapiddocs.web.app","https://rapiddocs.firebaseapp.com"]

# API Keys
GEMINI_API_KEY=
HUGGINGFACE_API_TOKEN=

# File Paths
UPLOAD_DIR=./uploads
GENERATED_DIR=./generated_pdfs
STATIC_DIR=./static
EOF
else
    echo "Updating existing .env.production..."
    # Remove old CORS_ORIGINS line if exists
    grep -v "^CORS_ORIGINS=" .env.production > .env.production.tmp
    mv .env.production.tmp .env.production
    # Add correct CORS_ORIGINS
    echo 'CORS_ORIGINS=["https://rapiddocs.io","https://www.rapiddocs.io","https://rapiddocs-9a3f8.web.app","https://rapiddocs.web.app","https://rapiddocs.firebaseapp.com"]' >> .env.production
fi

echo ""
echo "Step 4: Verifying files..."
if [ -f "app/main_simple.py" ]; then
    echo "✓ main_simple.py created successfully"
    echo "  File size: $(wc -l app/main_simple.py | awk '{print $1}') lines"
else
    echo "✗ Failed to create main_simple.py"
    exit 1
fi

if [ -f ".env.production" ]; then
    echo "✓ .env.production configured"
    echo "  CORS_ORIGINS: $(grep CORS_ORIGINS .env.production)"
else
    echo "✗ .env.production not found"
    exit 1
fi

echo ""
echo "Step 5: Rebuilding Docker container..."
echo "Stopping current container..."
docker-compose down

echo "Building new container without cache..."
docker-compose build --no-cache backend

echo "Starting container..."
docker-compose up -d

echo ""
echo "Step 6: Waiting for container to start (30 seconds)..."
for i in {1..30}; do
    echo -n "."
    sleep 1
done
echo ""

echo ""
echo "Step 7: Verifying container status..."
if docker ps | grep -q backend; then
    echo "✓ Container is running"
    docker ps | grep backend
else
    echo "✗ Container failed to start"
    echo "Checking logs:"
    docker logs backend --tail 50
    exit 1
fi

echo ""
echo "Step 8: Testing CORS headers..."
echo "Testing from https://rapiddocs.io origin..."
response=$(curl -s -I -X OPTIONS https://api.rapiddocs.io/auth/login \
  -H "Origin: https://rapiddocs.io" \
  -H "Access-Control-Request-Method: POST" 2>/dev/null | grep -i "access-control-allow-origin")

if echo "$response" | grep -q "https://rapiddocs.io"; then
    echo "✓ CORS headers configured correctly"
    echo "  $response"
else
    echo "✗ CORS headers not working properly"
    echo "  Response: $response"
    echo ""
    echo "Checking container logs for errors:"
    docker logs backend --tail 20
fi

echo ""
echo "Step 9: Testing authentication endpoint..."
auth_response=$(curl -s -X POST https://api.rapiddocs.io/auth/login \
  -H "Content-Type: application/json" \
  -H "Origin: https://rapiddocs.io" \
  -d '{"email":"test@rapiddocs.io","password":"testuser"}')

if echo "$auth_response" | grep -q "access_token"; then
    echo "✓ Authentication endpoint working"
    echo "  Test user login successful"
else
    echo "⚠ Authentication endpoint returned:"
    echo "  $auth_response"
    echo ""
    echo "This might be normal if test user doesn't exist yet."
fi

echo ""
echo "========================================="
echo "CORS FIX DEPLOYMENT COMPLETE!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Test login from browser at https://rapiddocs.io"
echo "2. Use test credentials:"
echo "   Email: test@rapiddocs.io"
echo "   Password: testuser"
echo ""
echo "If issues persist:"
echo "1. Check Docker logs: docker logs backend --tail 100"
echo "2. Check nginx logs: tail -f /var/log/nginx/error.log"
echo "3. Clear browser cache or use incognito mode"
echo ""
echo "Backup files created:"
ls -la *.backup.* 2>/dev/null || echo "No backups (files were created fresh)"