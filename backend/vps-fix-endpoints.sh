#!/bin/bash

# RapidDocs VPS Backend Fix - Update API Endpoints
# This script updates the backend to include all required API endpoints

set -e

echo "================================================"
echo "RapidDocs Backend VPS Fix - API Endpoints"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root or docgen user
if [[ $EUID -eq 0 ]] || [[ $USER == "docgen" ]]; then
    echo -e "${GREEN}Running as appropriate user${NC}"
else
    echo -e "${RED}This script must be run as root or docgen user${NC}"
    exit 1
fi

# VPS Configuration
BACKEND_DIR="/home/docgen/backend"

echo -e "${GREEN}Step 1: Navigating to backend directory...${NC}"
cd $BACKEND_DIR

echo -e "${GREEN}Step 2: Backing up current main_simple.py...${NC}"
cp app/main_simple.py app/main_simple.py.backup.$(date +%Y%m%d_%H%M%S) || true

echo -e "${GREEN}Step 3: Creating updated main_simple.py with all required endpoints...${NC}"
cat > app/main_simple.py << 'EOF'
"""
RapidDocs Backend - Simple Main Application
Includes all required endpoints for document generation
"""
import os
import sys
import json
import logging
import hashlib
import secrets
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Query, File, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security configurations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login", auto_error=False)

# JWT Settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "rapiddocs")

# Global database client
db_client = None
database = None

# Models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    referral_key: str

class AdminResponse(BaseModel):
    id: str
    username: str
    role: str
    created_at: datetime

class ReferralKeyResponse(BaseModel):
    key: str
    used: bool
    used_by: Optional[str]
    created_at: datetime

class DashboardStats(BaseModel):
    total_users: int
    total_documents: int
    referral_keys_used: int
    referral_keys_total: int

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

async def get_current_admin(token: Optional[str] = Depends(oauth2_scheme)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None

async def require_admin_auth(current_admin: Optional[TokenData] = Depends(get_current_admin)):
    if not current_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_admin

async def check_auth_or_frontend(current_admin: Optional[TokenData] = Depends(get_current_admin)):
    # For now, allow access without authentication
    # In production, this should check for valid auth or frontend origin
    return current_admin

# Lifespan context manager for database
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_client, database
    logger.info(f"Connecting to MongoDB at {MONGODB_URL}")
    db_client = AsyncIOMotorClient(MONGODB_URL)
    database = db_client[MONGODB_DB_NAME]

    # Create indexes
    await database.admins.create_index([("username", pymongo.ASCENDING)], unique=True)
    await database.referral_keys.create_index([("key", pymongo.ASCENDING)], unique=True)

    # Check for initial setup
    admin_count = await database.admins.count_documents({})
    if admin_count == 0:
        initial_key = secrets.token_urlsafe(16)
        await database.referral_keys.insert_one({
            "key": initial_key,
            "used": False,
            "used_by": None,
            "created_at": datetime.utcnow()
        })
        logger.info("=" * 50)
        logger.info("INITIAL SETUP - SAVE THIS INFORMATION!")
        logger.info(f"Initial Referral Key: {initial_key}")
        logger.info("=" * 50)

    yield

    # Shutdown
    if db_client:
        db_client.close()

# Create FastAPI app
app = FastAPI(
    title="RapidDocs API",
    version="2.0.0",
    description="Professional Document Generation Platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://rapiddocs.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Documentation endpoints (protected)
@app.get("/openapi.json", dependencies=[Depends(require_admin_auth)])
async def get_openapi():
    return app.openapi()

@app.get("/docs", dependencies=[Depends(require_admin_auth)])
async def get_documentation():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        <title>RapidDocs API - Documentation</title>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
        SwaggerUIBundle({
            url: '/openapi.json',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis]
        })
        </script>
    </body>
    </html>
    """)

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def docs_oauth2_redirect():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <body>
    <script>
        window.opener.swaggerUIRedirectOauth2 = {
            auth: window.location.hash.substr(1)
        };
        window.close();
    </script>
    </body>
    </html>
    """)

@app.get("/redoc", dependencies=[Depends(require_admin_auth)])
async def redoc_documentation():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RapidDocs API - ReDoc</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>body { margin: 0; padding: 0; }</style>
    </head>
    <body>
        <redoc spec-url="/openapi.json"></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """)

# Frontend pages
@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>RapidDocs API</h1><p>Backend is running. Visit <a href='/health'>/health</a> for status.</p>"

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return "<h1>Login</h1><p>Use the API endpoints for authentication.</p>"

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return "<h1>Register</h1><p>Use the API endpoints for registration.</p>"

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(current_admin: TokenData = Depends(require_admin_auth)):
    return f"<h1>Admin Dashboard</h1><p>Welcome, {current_admin.username}!</p>"

# Health check endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/detailed", dependencies=[Depends(check_auth_or_frontend)])
async def detailed_health():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "disconnected",
        "version": "2.0.0",
        "environment": os.getenv("APP_ENV", "production")
    }

    try:
        if database:
            await database.command("ping")
            health_status["database"] = "connected"

            # Get collection stats
            collections = await database.list_collection_names()
            health_status["collections"] = collections

            # Get document counts
            if "users" in collections:
                user_count = await database.users.count_documents({})
                health_status["user_count"] = user_count

            if "documents" in collections:
                doc_count = await database.documents.count_documents({})
                health_status["document_count"] = doc_count
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database_error"] = str(e)

    return health_status

@app.get("/health/ready")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    Returns 200 if the service is ready to accept traffic
    """
    try:
        # Check database connection
        if database:
            await database.command("ping")
            return {"ready": True, "timestamp": datetime.utcnow().isoformat()}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not connected"
            )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )

# Credits endpoints
@app.get("/credits/balance", dependencies=[Depends(check_auth_or_frontend)])
async def get_credits_balance():
    """Get current user's credit balance"""
    # Mock implementation - replace with actual logic
    return {"balance": 100, "currency": "credits"}

@app.post("/credits/deduct", dependencies=[Depends(check_auth_or_frontend)])
async def deduct_credits(document_type: str = Query(...)):
    """Deduct credits for document generation"""
    # Mock implementation - replace with actual logic
    credit_costs = {
        "invoice": 10,
        "infographic": 15,
        "formal": 5
    }
    cost = credit_costs.get(document_type, 10)
    return {
        "success": True,
        "credits_deducted": cost,
        "remaining_balance": 90,
        "document_type": document_type
    }

@app.get("/credits/packages", dependencies=[Depends(check_auth_or_frontend)])
async def get_credit_packages():
    """Get available credit packages"""
    return {
        "packages": [
            {
                "id": "basic",
                "name": "Basic Package",
                "credits": 100,
                "price": 9.99,
                "currency": "USD"
            },
            {
                "id": "professional",
                "name": "Professional Package",
                "credits": 500,
                "price": 39.99,
                "currency": "USD",
                "popular": True
            },
            {
                "id": "enterprise",
                "name": "Enterprise Package",
                "credits": 2000,
                "price": 149.99,
                "currency": "USD"
            }
        ]
    }

# Document validation endpoint
@app.post("/validate/invoice", dependencies=[Depends(check_auth_or_frontend)])
async def validate_invoice(request: dict):
    """Validate invoice generation request"""
    # Mock validation - replace with actual validation logic
    required_fields = ["business_name", "client_name", "line_items"]

    errors = []
    for field in required_fields:
        if field not in request or not request[field]:
            errors.append(f"Missing required field: {field}")

    if errors:
        return {
            "valid": False,
            "errors": errors
        }

    return {
        "valid": True,
        "message": "Invoice request is valid",
        "estimated_generation_time": 10
    }

# Document generation endpoints
class GenerateDocumentRequest(BaseModel):
    document_type: str
    business_name: str
    client_name: Optional[str] = None
    line_items: Optional[List[Dict[str, Any]]] = None
    content: Optional[str] = None
    statistics: Optional[List[Dict[str, Any]]] = None
    output_format: str = "pdf"

@app.post("/generate/document", dependencies=[Depends(check_auth_or_frontend)])
async def generate_document(request: GenerateDocumentRequest):
    """Generate a document (invoice, infographic, or formal)"""
    # Mock generation - replace with actual generation logic
    job_id = secrets.token_urlsafe(16)

    # Store job in database (mock)
    job = {
        "id": job_id,
        "type": request.document_type,
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
        "estimated_completion": (datetime.utcnow() + timedelta(seconds=30)).isoformat()
    }

    return {
        "job_id": job_id,
        "status": "processing",
        "message": f"Generating {request.document_type} document",
        "estimated_completion_time": 30
    }

@app.get("/generate/status/{job_id}", dependencies=[Depends(check_auth_or_frontend)])
async def get_generation_status(job_id: str):
    """Get document generation job status"""
    # Mock status - replace with actual status check
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "message": "Document generated successfully",
        "download_url": f"/generate/download/{job_id}"
    }

@app.get("/generate/download/{job_id}", dependencies=[Depends(check_auth_or_frontend)])
async def download_generated_document(job_id: str):
    """Download generated document"""
    # Mock file response - replace with actual file serving
    # For now, return a simple text file
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    temp_file.write(f"Generated document for job {job_id}\n")
    temp_file.write("This is a mock document.\n")
    temp_file.close()

    return FileResponse(
        temp_file.name,
        media_type="application/octet-stream",
        filename=f"document_{job_id}.txt"
    )

# Admin routes
@app.post("/admin/login", response_model=Token)
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Admin login endpoint"""
    if not database:
        raise HTTPException(status_code=500, detail="Database not connected")

    admin = await database.admins.find_one({"username": form_data.username})
    if not admin or not verify_password(form_data.password, admin["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": admin["username"], "role": admin["role"]})
    refresh_token = create_refresh_token(data={"sub": admin["username"]})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/admin/register", response_model=AdminResponse)
async def admin_register(admin_data: AdminCreate):
    """Register new admin with referral key"""
    if not database:
        raise HTTPException(status_code=500, detail="Database not connected")

    # Check referral key
    referral_key = await database.referral_keys.find_one({"key": admin_data.referral_key})
    if not referral_key:
        raise HTTPException(status_code=400, detail="Invalid referral key")
    if referral_key["used"]:
        raise HTTPException(status_code=400, detail="Referral key already used")

    # Create admin
    admin = {
        "username": admin_data.username,
        "password": get_password_hash(admin_data.password),
        "role": "admin",
        "created_at": datetime.utcnow()
    }

    try:
        result = await database.admins.insert_one(admin)

        # Mark referral key as used
        await database.referral_keys.update_one(
            {"key": admin_data.referral_key},
            {"$set": {"used": True, "used_by": admin_data.username}}
        )

        return AdminResponse(
            id=str(result.inserted_id),
            username=admin["username"],
            role=admin["role"],
            created_at=admin["created_at"]
        )
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Username already exists")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

echo -e "${GREEN}Step 4: Stopping current Docker containers...${NC}"
docker-compose down || true

echo -e "${GREEN}Step 5: Rebuilding Docker image with updated code...${NC}"
docker-compose build --no-cache

echo -e "${GREEN}Step 6: Starting updated containers...${NC}"
docker-compose up -d

echo -e "${GREEN}Step 7: Waiting for service to start...${NC}"
sleep 10

echo -e "${GREEN}Step 8: Testing health endpoint...${NC}"
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
fi

echo -e "${GREEN}Step 9: Testing required endpoints...${NC}"
echo "Testing /validate/invoice endpoint..."
curl -X POST http://localhost:8000/validate/invoice \
     -H "Content-Type: application/json" \
     -d '{"business_name":"Test","client_name":"Client","line_items":[]}' \
     -w "\nHTTP Status: %{http_code}\n" || true

echo ""
echo "Testing /credits/deduct endpoint..."
curl -X POST "http://localhost:8000/credits/deduct?document_type=invoice" \
     -w "\nHTTP Status: %{http_code}\n" || true

echo ""
echo -e "${GREEN}Step 10: Checking container logs...${NC}"
docker-compose logs --tail=30

echo ""
echo "================================================"
echo -e "${GREEN}VPS Backend Fix Complete!${NC}"
echo "================================================"
echo ""
echo "The following endpoints should now be available:"
echo "- POST https://api.rapiddocs.io/validate/invoice"
echo "- POST https://api.rapiddocs.io/credits/deduct"
echo "- GET  https://api.rapiddocs.io/credits/balance"
echo "- GET  https://api.rapiddocs.io/credits/packages"
echo "- POST https://api.rapiddocs.io/generate/document"
echo "- GET  https://api.rapiddocs.io/generate/status/{job_id}"
echo "- GET  https://api.rapiddocs.io/generate/download/{job_id}"
echo ""
echo "Test from your browser console or with curl:"
echo "curl https://api.rapiddocs.io/health"
echo ""
echo "If you see any issues, check logs with:"
echo "docker-compose logs -f"