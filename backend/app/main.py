from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import documents, generation, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()

    # Create necessary directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)

    yield

    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered document generation API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists(settings.PDF_OUTPUT_DIR):
    app.mount("/pdfs", StaticFiles(directory=settings.PDF_OUTPUT_DIR), name="pdfs")

# Include routers
app.include_router(documents.router, prefix=settings.API_PREFIX, tags=["documents"])
app.include_router(generation.router, prefix=settings.API_PREFIX, tags=["generation"])
app.include_router(upload.router, prefix=settings.API_PREFIX, tags=["upload"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Serve frontend static files (for production deployment)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    # Serve index.html for all other routes (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # If it's an API route, let it pass through
        if full_path.startswith("api/"):
            return {"error": "Not found"}

        # Check if file exists in static directory
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # Otherwise serve index.html (for SPA routing)
        index_path = os.path.join(static_dir, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)

        return {"error": "Not found"}
else:
    # Fallback for development mode
    @app.get("/")
    async def root():
        return {
            "message": "Document Generator API",
            "version": "1.0.0",
            "docs": f"{settings.API_PREFIX}/docs"
        }
