from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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

from app.config import settings
from app.services.gemini_service import GeminiService
from app.services.pdf_service import PDFService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create necessary directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)
    os.makedirs(Path(settings.PDF_OUTPUT_DIR) / "invoices", exist_ok=True)
    os.makedirs(Path(settings.UPLOAD_DIR) / "logos", exist_ok=True)

    # Initialize services
    app.state.gemini_service = GeminiService()
    app.state.pdf_service = PDFService()
    logger.info("Services initialized successfully")

    yield

    # Shutdown
    pass


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered document generation API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists(settings.PDF_OUTPUT_DIR):
    app.mount("/pdfs", StaticFiles(directory=settings.PDF_OUTPUT_DIR), name="pdfs")


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service status."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gemini": "operational",
            "pdf_generator": "operational",
            "storage": "operational"
        },
        "directories": {
            "upload_dir": os.path.exists(settings.UPLOAD_DIR),
            "pdf_output_dir": os.path.exists(settings.PDF_OUTPUT_DIR)
        },
        "environment": settings.APP_ENV,
        "version": "1.0.0"
    }

    # Check if Gemini service is initialized
    try:
        if hasattr(app.state, 'gemini_service'):
            health_status["services"]["gemini"] = "operational"
        else:
            health_status["services"]["gemini"] = "not_initialized"
            health_status["status"] = "degraded"
    except:
        health_status["services"]["gemini"] = "error"
        health_status["status"] = "degraded"

    # Check if PDF service is initialized
    try:
        if hasattr(app.state, 'pdf_service'):
            health_status["services"]["pdf_generator"] = "operational"
        else:
            health_status["services"]["pdf_generator"] = "not_initialized"
            health_status["status"] = "degraded"
    except:
        health_status["services"]["pdf_generator"] = "error"
        health_status["status"] = "degraded"

    return health_status


@app.get("/health/ready")
async def readiness_check():
    """Readiness probe for Kubernetes/monitoring."""
    # Check if all services are ready
    is_ready = True
    issues = []

    if not hasattr(app.state, 'gemini_service'):
        is_ready = False
        issues.append("Gemini service not initialized")

    if not hasattr(app.state, 'pdf_service'):
        is_ready = False
        issues.append("PDF service not initialized")

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


# Credits endpoints
@app.get("/credits/balance")
async def get_credit_balance():
    """Get current credit balance."""
    return {
        "credits": 1000,
        "message": "Development mode - unlimited credits"
    }


@app.post("/credits/deduct")
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


@app.get("/credits/packages")
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


# Invoice validation endpoint
@app.post("/validate/invoice")
async def validate_invoice_prompt(description: str = Form(...)):
    """Validate if the user prompt has enough information for invoice generation."""
    try:
        gemini_service = app.state.gemini_service

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


# Document generation endpoint with actual PDF generation
@app.post("/generate/document")
async def generate_document(
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
            gemini_service = app.state.gemini_service
            pdf_service = app.state.pdf_service

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


@app.get("/generate/status/{job_id}")
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


@app.get("/generate/download/{job_id}")
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


# API-only deployment - no frontend serving
# Frontend is hosted separately on Firebase

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "RapidDocs Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "environment": settings.APP_ENV
    }