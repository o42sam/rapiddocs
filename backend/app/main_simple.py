from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import os
import json
import uuid
from pathlib import Path
from datetime import datetime
import logging
import cairosvg
from PIL import Image
import io
import motor.motor_asyncio
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.services.gemini_service import GeminiService
from app.services.pdf_service import PDFService
from app.services.auth_service import AuthService
from app.routes import admin, user_auth
from app.middleware.auth import AuthMiddleware, security

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Templates for HTML pages
templates = Jinja2Templates(directory="app/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create necessary directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)
    os.makedirs(Path(settings.PDF_OUTPUT_DIR) / "invoices", exist_ok=True)
    os.makedirs(Path(settings.UPLOAD_DIR) / "logos", exist_ok=True)

    # Initialize MongoDB connection
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db = client[settings.MONGODB_DB_NAME]

    # Initialize services
    app.state.gemini_service = GeminiService()
    app.state.pdf_service = PDFService()
    app.state.auth_service = AuthService(app.state.db)
    app.state.auth_middleware = AuthMiddleware(app.state.auth_service)
    app.state.start_time = datetime.utcnow()

    logger.info("Services initialized successfully")

    # Create initial superuser if none exists
    initial_creds = await app.state.auth_service.create_initial_superuser()
    if initial_creds:
        logger.info("=" * 60)
        logger.info("INITIAL SETUP - SAVE THIS INFORMATION!")
        logger.info(f"Initial referral key created: {initial_creds[1]}")
        logger.info("Use this key to register the first superuser admin")
        logger.info("Access registration at: https://api.rapiddocs.io/register")
        logger.info("=" * 60)

    yield

    # Shutdown
    client.close()


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered document generation API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,  # Disable automatic docs
    redoc_url=None,  # Disable automatic redoc
    openapi_url=None  # Disable automatic openapi
)

# CORS - Use settings or fallback to hardcoded
# Strip whitespace from each origin to avoid matching issues
raw_origins = settings.CORS_ORIGINS.split(",") if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS else []
cors_origins = [origin.strip() for origin in raw_origins] if raw_origins else []

# Always include these origins
default_origins = [
    "https://rapiddocs.io",
    "https://www.rapiddocs.io",
    "https://rapiddocs-9a3f8.web.app",
    "https://rapiddocs.web.app",
    "https://rapiddocs.firebaseapp.com",
    "http://localhost:5173",
    "http://localhost:5174"
]

# Merge and deduplicate
for origin in default_origins:
    if origin not in cors_origins:
        cors_origins.append(origin)

logger.info(f"CORS origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Mount static files
if os.path.exists(settings.PDF_OUTPUT_DIR):
    app.mount("/pdfs", StaticFiles(directory=settings.PDF_OUTPUT_DIR), name="pdfs")

# Include routers
app.include_router(admin.router)
app.include_router(user_auth.router)


# Authentication check dependency
async def check_auth_or_frontend(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Check if request is authenticated or from allowed frontend."""
    # Check if request is from allowed frontend origin
    origin = request.headers.get("origin", "")
    referer = request.headers.get("referer", "")

    allowed_origins = cors_origins  # Use the same origins as CORS config

    # If request is from allowed frontend, allow it
    for allowed in allowed_origins:
        if origin.startswith(allowed) or referer.startswith(allowed):
            return None

    # Otherwise, require admin authentication
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    auth_service = request.app.state.auth_service
    token_data = auth_service.decode_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    admin = await auth_service.get_admin_by_username(token_data.get("username"))
    if not admin or not admin.is_active:
        raise HTTPException(status_code=401, detail="Admin user not found or inactive")

    return admin


# Admin authentication only (no frontend bypass)
async def require_admin_auth(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Require admin authentication for sensitive endpoints."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    auth_service = request.app.state.auth_service
    token_data = auth_service.decode_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    admin = await auth_service.get_admin_by_username(token_data.get("username"))
    if not admin or not admin.is_active:
        raise HTTPException(status_code=401, detail="Admin user not found or inactive")

    return admin


# Protected OpenAPI endpoints
@app.get("/openapi.json", dependencies=[Depends(require_admin_auth)])
async def get_openapi():
    """Get OpenAPI schema (requires admin auth)."""
    from fastapi.openapi.utils import get_openapi
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
    return app.openapi_schema


@app.get("/docs", dependencies=[Depends(require_admin_auth)])
async def custom_swagger_ui_html(request: Request):
    """Swagger UI documentation (requires admin auth)."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=str(request.url_for("swagger_ui_redirect")),
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    """OAuth2 redirect for Swagger UI."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", dependencies=[Depends(require_admin_auth)])
async def redoc_html(request: Request):
    """ReDoc documentation (requires admin auth)."""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js",
    )


# HTML Pages (no auth required for login/register)
@app.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    """Redirect to login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve registration page."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Serve admin dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


# Health endpoints (no auth required for Docker health checks)
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/health/detailed", dependencies=[Depends(check_auth_or_frontend)])
async def detailed_health_check(request: Request):
    """Detailed health check with service status."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gemini": "operational",
            "pdf_generator": "operational",
            "storage": "operational",
            "database": "operational",
            "auth": "operational"
        },
        "directories": {
            "upload_dir": os.path.exists(settings.UPLOAD_DIR),
            "pdf_output_dir": os.path.exists(settings.PDF_OUTPUT_DIR)
        },
        "environment": settings.APP_ENV,
        "version": "1.0.0"
    }

    # Check if services are initialized
    try:
        if hasattr(request.app.state, 'gemini_service'):
            health_status["services"]["gemini"] = "operational"
        else:
            health_status["services"]["gemini"] = "not_initialized"
            health_status["status"] = "degraded"
    except:
        health_status["services"]["gemini"] = "error"
        health_status["status"] = "degraded"

    try:
        if hasattr(request.app.state, 'pdf_service'):
            health_status["services"]["pdf_generator"] = "operational"
        else:
            health_status["services"]["pdf_generator"] = "not_initialized"
            health_status["status"] = "degraded"
    except:
        health_status["services"]["pdf_generator"] = "error"
        health_status["status"] = "degraded"

    try:
        if hasattr(request.app.state, 'db'):
            # Test database connection
            await request.app.state.db.command('ping')
            health_status["services"]["database"] = "operational"
        else:
            health_status["services"]["database"] = "not_initialized"
            health_status["status"] = "degraded"
    except:
        health_status["services"]["database"] = "error"
        health_status["status"] = "degraded"

    return health_status


@app.get("/health/ready")
async def readiness_check(request: Request):
    """Readiness probe for Kubernetes/monitoring."""
    # Check if all services are ready
    is_ready = True
    issues = []

    if not hasattr(request.app.state, 'gemini_service'):
        is_ready = False
        issues.append("Gemini service not initialized")

    if not hasattr(request.app.state, 'pdf_service'):
        is_ready = False
        issues.append("PDF service not initialized")

    if not hasattr(request.app.state, 'db'):
        is_ready = False
        issues.append("Database not initialized")

    if not os.path.exists(settings.UPLOAD_DIR):
        is_ready = False
        issues.append("Upload directory not found")

    if not os.path.exists(settings.PDF_OUTPUT_DIR):
        is_ready = False
        issues.append("PDF output directory not found")

    if is_ready:
        return {"status": "ready", "timestamp": datetime.now().isoformat()}
    else:
        raise HTTPException(status_code=503, detail={"status": "not_ready", "issues": issues})


# Credits endpoints (protected)
@app.get("/credits/balance", dependencies=[Depends(check_auth_or_frontend)])
async def get_credit_balance():
    """Get current credit balance."""
    return {
        "credits": 1000,
        "message": "Development mode - unlimited credits"
    }


@app.post("/credits/deduct", dependencies=[Depends(check_auth_or_frontend)])
async def deduct_credits(document_type: str):
    """Deduct credits for document generation."""
    credit_costs = {
        "invoice": 1,
        "infographic": 2,
        "formal": 1,
    }

    cost = credit_costs.get(document_type, 1)

    return {
        "message": f"Credits deducted for {document_type}",
        "credits_deducted": cost,
        "new_balance": 999
    }


@app.get("/credits/packages", dependencies=[Depends(check_auth_or_frontend)])
async def get_credit_packages():
    """Get available credit packages."""
    return {
        "packages": [
            {
                "id": "basic",
                "name": "Basic",
                "credits": 10,
                "price": 9.99,
                "currency": "USD"
            },
            {
                "id": "standard",
                "name": "Standard",
                "credits": 50,
                "price": 39.99,
                "currency": "USD"
            },
            {
                "id": "premium",
                "name": "Premium",
                "credits": 100,
                "price": 69.99,
                "currency": "USD"
            }
        ]
    }


# Invoice validation endpoint (protected)
@app.post("/validate/invoice", dependencies=[Depends(check_auth_or_frontend)])
async def validate_invoice_prompt(request: Request, description: str = Form(...)):
    """Validate if the user prompt has enough information for invoice generation."""
    try:
        gemini_service = request.app.state.gemini_service

        # Extract invoice data from the prompt
        invoice_data = await gemini_service.extract_invoice_data(description, "invoice")

        # Validate completeness
        is_complete, missing_fields = gemini_service.validate_invoice_completeness(invoice_data)

        return {
            "is_complete": is_complete,
            "missing_fields": missing_fields,
            "extracted_data": invoice_data,
            "message": "Invoice data validation complete"
        }
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}", exc_info=True)
        return {
            "is_complete": False,
            "missing_fields": ["Unable to validate - please try again"],
            "extracted_data": {},
            "message": str(e)
        }


# Document generation endpoint (protected)
@app.post("/generate/document", dependencies=[Depends(check_auth_or_frontend)])
async def generate_document(
    request: Request,
    description: str = Form(...),
    length: int = Form(500),
    document_type: str = Form(...),
    use_watermark: bool = Form(False),
    statistics: str = Form("[]"),
    design_spec: str = Form("{}"),
    logo: Optional[UploadFile] = File(None),
    skip_validation: bool = Form(False)
):
    """Generate a document with actual PDF output."""
    try:
        # Parse design spec and statistics
        try:
            design = json.loads(design_spec) if design_spec else {}
        except:
            design = {}

        try:
            stats = json.loads(statistics) if statistics else []
        except:
            stats = []

        # Generate a unique job ID
        job_id = f"{document_type.upper()}-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

        # Handle different document types
        if document_type == "invoice":
            # Use Gemini to extract invoice data from the user's description
            gemini_service = request.app.state.gemini_service
            pdf_service = request.app.state.pdf_service

            logger.info(f"Processing invoice generation for job {job_id}")
            logger.info(f"User description: {description}")

            # Extract invoice data using Gemini
            invoice_data = await gemini_service.extract_invoice_data(description, document_type)

            # Validate the extracted data unless validation is skipped
            if not skip_validation:
                is_complete, missing_fields = gemini_service.validate_invoice_completeness(invoice_data)
                if not is_complete:
                    logger.warning(f"Invoice data incomplete. Missing: {', '.join(missing_fields)}")
                    # Don't generate PDF yet - let frontend decide
                    return {
                        "job_id": job_id,
                        "status": "validation_failed",
                        "message": "Invoice data is incomplete",
                        "missing_fields": missing_fields,
                        "extracted_data": invoice_data,
                        "document_type": document_type,
                        "credits_used": 0
                    }
            else:
                # If skip_validation is True, log that we're proceeding despite incomplete data
                logger.info(f"Skipping validation for job {job_id} - proceeding with generation")

            # Override with any provided design specs
            if design:
                for key, value in design.items():
                    if key in invoice_data and value:
                        invoice_data[key] = value

            # Set the invoice number to match our job ID
            invoice_data["invoice_number"] = job_id

            # Handle logo upload if provided
            logo_path = None
            if logo:
                logo_dir = Path(settings.UPLOAD_DIR) / "logos"
                logo_dir.mkdir(parents=True, exist_ok=True)

                content = await logo.read()

                # Check if the uploaded file is SVG
                if logo.filename.lower().endswith('.svg'):
                    # Convert SVG to PNG
                    png_filename = f"{job_id}_logo.png"
                    logo_path = logo_dir / png_filename

                    try:
                        # Convert SVG to PNG using cairosvg
                        png_data = cairosvg.svg2png(bytestring=content, output_width=400, output_height=200)

                        # Save the PNG file
                        with open(logo_path, "wb") as f:
                            f.write(png_data)
                        logger.info(f"SVG logo converted to PNG and saved to {logo_path}")
                    except Exception as e:
                        logger.error(f"Failed to convert SVG to PNG: {e}")
                        # Fall back to saving original file
                        logo_path = logo_dir / f"{job_id}_{logo.filename}"
                        with open(logo_path, "wb") as f:
                            f.write(content)
                else:
                    # For non-SVG files, save as-is
                    logo_path = logo_dir / f"{job_id}_{logo.filename}"
                    with open(logo_path, "wb") as f:
                        f.write(content)
                    logger.info(f"Logo saved to {logo_path}")

            # Generate the PDF
            output_dir = Path(settings.PDF_OUTPUT_DIR) / "invoices"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{job_id}.pdf"

            logger.info(f"Generating PDF for invoice {job_id}")
            pdf_path = await pdf_service.generate_invoice_pdf(
                invoice_data=invoice_data,
                output_path=output_path,
                logo_path=logo_path
            )

            logger.info(f"PDF generated successfully at {pdf_path}")

            # Log document generation to database
            await request.app.state.db.generation_jobs.insert_one({
                "job_id": job_id,
                "document_type": document_type,
                "created_at": datetime.utcnow(),
                "status": "completed",
                "user_ip": request.client.host if request.client else None
            })

            return {
                "job_id": job_id,
                "status": "completed",
                "message": "Invoice generated successfully",
                "download_url": f"/generate/download/{job_id}",
                "document_type": document_type,
                "credits_used": 1
            }

        elif document_type == "infographic":
            # Placeholder for infographic generation
            return {
                "job_id": f"INFOGRAPHIC-{uuid.uuid4().hex[:8]}",
                "status": "pending",
                "message": "Infographic generation coming soon",
                "document_type": "infographic",
                "credits_used": 2
            }

        elif document_type == "formal":
            # Placeholder for formal document generation
            return {
                "job_id": f"FORMAL-{uuid.uuid4().hex[:8]}",
                "status": "pending",
                "message": "Formal document generation coming soon",
                "document_type": "formal",
                "credits_used": 1
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown document type: {document_type}")

    except Exception as e:
        logger.error(f"Document generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/generate/status/{job_id}", dependencies=[Depends(check_auth_or_frontend)])
async def get_job_status(job_id: str):
    """Get generation job status."""
    # Check if the PDF exists
    invoice_dir = Path(settings.PDF_OUTPUT_DIR) / "invoices"
    pdf_path = invoice_dir / f"{job_id}.pdf"

    if pdf_path.exists():
        return {
            "job_id": job_id,
            "status": "completed",
            "progress": 100,
            "current_step": "completed",
            "message": "Document ready for download"
        }
    else:
        # Check if there's a validation failure (no PDF generated)
        return {
            "job_id": job_id,
            "status": "failed",
            "progress": 0,
            "current_step": "validation_failed",
            "error_message": "Document generation was not completed. Please retry with complete information.",
            "message": "Document generation incomplete"
        }


@app.get("/generate/download/{job_id}", dependencies=[Depends(check_auth_or_frontend)])
async def download_generated_document(job_id: str):
    """Download generated document PDF."""
    try:
        # Look for the PDF in the invoices directory
        invoice_dir = Path(settings.PDF_OUTPUT_DIR) / "invoices"
        pdf_path = invoice_dir / f"{job_id}.pdf"

        if pdf_path.exists():
            logger.info(f"Serving PDF: {pdf_path}")
            return FileResponse(
                path=str(pdf_path),
                media_type="application/pdf",
                filename=f"{job_id}.pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={job_id}.pdf"
                }
            )

        # Fallback: Try to find any matching PDF
        matching_files = list(invoice_dir.glob(f"*{job_id}*.pdf"))
        if matching_files:
            pdf_path = matching_files[0]
            logger.info(f"Serving matching PDF: {pdf_path}")
            return FileResponse(
                path=str(pdf_path),
                media_type="application/pdf",
                filename=pdf_path.name,
                headers={
                    "Content-Disposition": f"attachment; filename={pdf_path.name}"
                }
            )

        # Try general documents directory
        general_dir = Path(settings.PDF_OUTPUT_DIR)
        pdf_path = general_dir / f"{job_id}.pdf"
        if pdf_path.exists():
            logger.info(f"Serving PDF from general dir: {pdf_path}")
            return FileResponse(
                path=str(pdf_path),
                media_type="application/pdf",
                filename=f"{job_id}.pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={job_id}.pdf"
                }
            )

        logger.error(f"PDF not found for job_id: {job_id}")
        raise HTTPException(status_code=404, detail="Document not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))