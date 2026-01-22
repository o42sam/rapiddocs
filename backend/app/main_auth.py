"""
Clean Architecture FastAPI Application with Authentication
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# Import domain interfaces
from app.domain.interfaces.user_repository import IUserRepository
from app.domain.interfaces.auth_service import IAuthService

# Import infrastructure implementations
from app.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository
from app.infrastructure.persistence.mongodb_user_repository import MongoDBUserRepository
from app.infrastructure.persistence.database import connect_to_mongo, close_mongo_connection, get_database
from app.infrastructure.auth.jwt_auth_service import JWTAuthService

# Import application use cases
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.login_user import LoginUserUseCase

# Import presentation routes
from app.presentation.routes import auth_routes
from app.presentation.routes import invoice_routes
from app.presentation.routes import credits_routes
from app.presentation.routes import generation_routes

# Global instances (in production, use proper dependency injection container)
user_repository: IUserRepository = None
auth_service: IAuthService = None
register_use_case: RegisterUserUseCase = None
login_use_case: LoginUserUseCase = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting RapidDocs with Authentication...")

    # Connect to MongoDB
    await connect_to_mongo()

    # Initialize repositories and services
    global user_repository, auth_service, register_use_case, login_use_case

    # Use MongoDB repository if connected, fallback to in-memory
    try:
        database = get_database()
        user_repository = MongoDBUserRepository(database)
        print("✅ Using MongoDB for user persistence")
    except Exception as e:
        print(f"⚠️ MongoDB not available: {e}")
        print("⚠️ Falling back to in-memory repository")
        user_repository = InMemoryUserRepository()

    # Initialize auth service with JWT
    auth_service = JWTAuthService(
        user_repository=user_repository,
        secret_key=os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production"),
        algorithm="HS256",
        access_token_expire_minutes=60,
        refresh_token_expire_days=7
    )

    # Initialize use cases
    register_use_case = RegisterUserUseCase(
        user_repository=user_repository,
        auth_service=auth_service
    )

    login_use_case = LoginUserUseCase(
        user_repository=user_repository,
        auth_service=auth_service
    )

    # Create necessary directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)

    print("Authentication system initialized successfully!")

    yield

    # Shutdown
    print("Shutting down RapidDocs...")
    await close_mongo_connection()


app = FastAPI(
    title="RapidDocs - Clean Architecture with Auth",
    description="AI-powered document generation API with authentication",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection overrides
def get_user_repository() -> IUserRepository:
    """Get user repository instance"""
    return user_repository


def get_auth_service() -> IAuthService:
    """Get auth service instance"""
    return auth_service


def get_register_use_case() -> RegisterUserUseCase:
    """Get register use case instance"""
    return register_use_case


def get_login_use_case() -> LoginUserUseCase:
    """Get login use case instance"""
    return login_use_case


# Override FastAPI dependency injection
from fastapi import Depends

app.dependency_overrides[auth_routes.get_auth_service] = get_auth_service
app.dependency_overrides[auth_routes.get_register_use_case] = get_register_use_case
app.dependency_overrides[auth_routes.get_login_use_case] = get_login_use_case

# Include auth routes
app.include_router(
    auth_routes.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# Include invoice routes
app.include_router(
    invoice_routes.router,
    prefix="/api/v1/invoice",
    tags=["Invoice Generation"]
)

# Include credits routes
app.include_router(
    credits_routes.router,
    prefix="/api/v1/credits",
    tags=["Credits Management"]
)

# Include generation routes (unified endpoint for all document types)
app.include_router(
    generation_routes.router,
    prefix="/api/v1/generate",
    tags=["Document Generation"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "architecture": "clean",
        "version": "2.1.0",
        "features": ["authentication"]
    }


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "message": "Clean Architecture with Authentication",
        "endpoints": {
            "health": "/health",
            "docs": "/api/v1/docs",
            "auth": {
                "register": "/api/v1/auth/register",
                "login": "/api/v1/auth/login",
                "refresh": "/api/v1/auth/refresh",
                "logout": "/api/v1/auth/logout",
                "current_user": "/api/v1/auth/me"
            },
            "documents": {
                "invoice": {
                    "generate": "/api/v1/invoice/generate",
                    "download": "/api/v1/invoice/download/{invoice_id}",
                    "import_data": "/api/v1/invoice/import-data",
                    "templates": "/api/v1/invoice/templates"
                },
                "infographic": "Coming soon - /api/v1/infographic/generate",
                "formal": "Coming soon - /api/v1/formal/generate"
            }
        }
    }


# Serve frontend static files if they exist
static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(static_dir):
    # Mount assets directory
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Serve root
    @app.get("/")
    async def serve_root():
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not built. Run 'npm run build' in frontend directory."}

    # Catch-all route for SPA
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't interfere with API routes
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}

        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Frontend not found"}
else:
    @app.get("/")
    async def root():
        return {
            "message": "RapidDocs Backend API - Clean Architecture with Authentication",
            "docs": "/api/v1/docs",
            "health": "/health"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)