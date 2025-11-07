from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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


@app.get("/")
async def root():
    return {
        "message": "Document Generator API",
        "version": "1.0.0",
        "docs": f"{settings.API_PREFIX}/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
