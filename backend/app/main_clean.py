"""
Clean Architecture FastAPI Application
Temporary main file for testing after restructuring
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting RapidDocs Clean Architecture...")

    # Create necessary directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)

    yield

    # Shutdown
    print("Shutting down RapidDocs...")


app = FastAPI(
    title="RapidDocs - Clean Architecture",
    description="AI-powered document generation API (Clean Architecture)",
    version="2.0.0",
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "architecture": "clean",
        "version": "2.0.0"
    }


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "message": "Clean Architecture implementation in progress",
        "endpoints": {
            "health": "/health",
            "docs": "/api/v1/docs",
            "invoice": "Coming soon - /api/v1/invoice/generate",
            "infographic": "Coming soon - /api/v1/infographic/generate",
            "formal": "Coming soon - /api/v1/formal/generate"
        }
    }


# Temporary endpoints for testing
@app.post("/api/v1/invoice/generate")
async def generate_invoice():
    """Placeholder for invoice generation"""
    return {
        "status": "pending",
        "message": "Invoice generation will be available once use cases are wired up",
        "architecture_layer": "presentation -> application -> domain -> infrastructure"
    }


@app.post("/api/v1/infographic/generate")
async def generate_infographic():
    """Placeholder for infographic generation"""
    return {
        "status": "pending",
        "message": "Infographic generation will be available once use cases are wired up",
        "architecture_layer": "presentation -> application -> domain -> infrastructure"
    }


@app.post("/api/v1/formal/generate")
async def generate_formal():
    """Placeholder for formal document generation"""
    return {
        "status": "pending",
        "message": "Formal document generation will be available once use cases are wired up",
        "architecture_layer": "presentation -> application -> domain -> infrastructure"
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
            "message": "RapidDocs Backend API - Clean Architecture",
            "docs": "/api/v1/docs",
            "health": "/health"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)