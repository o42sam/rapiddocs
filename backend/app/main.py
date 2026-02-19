from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.config import settings
# from app.database import connect_to_mongo, close_mongo_connection
# Routes
from app.presentation.routes import infographic_routes, invoice_routes, generation_routes, credits_routes
import asyncio

# Debug: Print environment variables at startup
print("=" * 50)
print("ENVIRONMENT VARIABLES DEBUG")
print("=" * 50)
print(f"MONGODB_URL: {'SET' if settings.MONGODB_URL else 'NOT SET'} (length: {len(settings.MONGODB_URL)})")
print(f"MONGODB_DB_NAME: {settings.MONGODB_DB_NAME}")
print(f"DISABLE_MONGODB: {settings.DISABLE_MONGODB}")
print(f"HUGGINGFACE_API_KEY: {'SET' if settings.HUGGINGFACE_API_KEY else 'NOT SET'} (length: {len(settings.HUGGINGFACE_API_KEY)})")
print(f"APP_ENV: {settings.APP_ENV}")
print(f"DEBUG: {settings.DEBUG}")
print("=" * 50)

# Also check raw environment variables
print("RAW OS ENVIRONMENT VARIABLES:")
print(f"os.environ.get('MONGODB_URL'): {'SET' if os.environ.get('MONGODB_URL') else 'NOT SET'}")
print(f"os.environ.get('HUGGINGFACE_API_KEY'): {'SET' if os.environ.get('HUGGINGFACE_API_KEY') else 'NOT SET'}")
print("=" * 50)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # await connect_to_mongo()

    # Create necessary directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)

    # Start Bitcoin payment background processor
    # processor_task = asyncio.create_task(bitcoin_payment_processor.start_background_processor())

    yield

    # Shutdown
    # bitcoin_payment_processor.stop_background_processor()
    # await close_mongo_connection()


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
app.include_router(infographic_routes.router, prefix=settings.API_PREFIX)
app.include_router(invoice_routes.router, prefix=f"{settings.API_PREFIX}/invoice", tags=["invoices"])
app.include_router(generation_routes.router, prefix=settings.API_PREFIX)
app.include_router(credits_routes.router, prefix=f"{settings.API_PREFIX}/credits", tags=["credits"])
# app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["authentication"])
# app.include_router(admin.router, prefix=f"{settings.API_PREFIX}/admin", tags=["admin"])
# app.include_router(bitcoin.router, prefix=f"{settings.API_PREFIX}/bitcoin", tags=["bitcoin-payments"])
# app.include_router(paystack.router, prefix=settings.API_PREFIX, tags=["paystack-payments"])
# app.include_router(documents.router, prefix=settings.API_PREFIX, tags=["documents"])
# app.include_router(generation.router, prefix=settings.API_PREFIX, tags=["generation"])
# app.include_router(upload.router, prefix=settings.API_PREFIX, tags=["upload"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post(f"{settings.API_PREFIX}/validate/invoice")
async def validate_invoice_prompt(description: str = Form(...)):
    """Validate if the user prompt has enough information for invoice generation."""
    missing_fields = []
    desc_lower = description.lower()

    # Check for key invoice fields mentioned in the prompt
    if not any(word in desc_lower for word in ["client", "customer", "bill to", "recipient"]):
        missing_fields.append("client_name")
    if not any(word in desc_lower for word in ["company", "vendor", "from", "business", "seller"]):
        missing_fields.append("vendor_name")
    if not any(char.isdigit() for char in description):
        missing_fields.append("line_items")

    return {
        "is_complete": len(missing_fields) == 0,
        "missing_fields": missing_fields,
        "message": "Invoice data validation complete"
    }


# Serve frontend static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    # Mount assets directory
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Serve root
    @app.get("/")
    async def serve_root():
        return FileResponse(os.path.join(static_dir, "index.html"))

    # Serve static files
    @app.get("/favicon.ico")
    async def serve_favicon():
        return FileResponse(os.path.join(static_dir, "favicon.ico"))

    @app.get("/logo.png")
    async def serve_logo():
        return FileResponse(os.path.join(static_dir, "logo.png"))

    @app.get("/rd-logo.svg")
    async def serve_rd_logo():
        return FileResponse(os.path.join(static_dir, "rd-logo.svg"))

    # Catch-all route for SPA (Single Page Application) routing
    # This must be last to allow other routes to match first
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Serve the SPA for all non-API routes.
        This allows client-side routing to work correctly.
        """
        # Don't interfere with API routes
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}

        # Serve index.html for all other routes
        return FileResponse(os.path.join(static_dir, "index.html"))
