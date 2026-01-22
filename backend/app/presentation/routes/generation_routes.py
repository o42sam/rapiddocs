"""
Generation API Routes.
Unified endpoint for all document generation types.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any
from pathlib import Path
import json
import logging

from .invoice_routes import get_invoice_use_case, GenerateInvoiceUseCase, cleanup_temp_file
from ...application.dto.invoice_request import InvoiceRequest
from ...config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/document")
async def generate_document(
    background_tasks: BackgroundTasks,
    description: str = Form(...),
    length: int = Form(500),
    document_type: str = Form(...),
    use_watermark: bool = Form(False),
    statistics: str = Form("[]"),
    design_spec: str = Form("{}"),
    logo: Optional[UploadFile] = File(None),
    invoice_use_case: GenerateInvoiceUseCase = Depends(get_invoice_use_case)
):
    """
    Unified document generation endpoint.
    Routes to appropriate handler based on document_type.
    """
    try:
        # Parse statistics and design spec
        try:
            stats = json.loads(statistics) if statistics else []
            design = json.loads(design_spec) if design_spec else {}
        except json.JSONDecodeError:
            stats = []
            design = {}

        # Route based on document type
        if document_type == "invoice":
            # Extract invoice-specific data from description or design spec
            invoice_data = {
                "invoice_number": design.get("invoice_number", f"INV-{Path.home().name}-001"),
                "client_name": design.get("client_name", "Client Company"),
                "vendor_name": design.get("vendor_name", "Your Company"),
                "description": description,
                "client_address": design.get("client_address", ""),
                "vendor_address": design.get("vendor_address", ""),
                "currency": design.get("currency", "USD"),
                "payment_terms": design.get("payment_terms", "Net 30"),
                "line_items": design.get("line_items", []),
                "ai_generate_items": True,
                "ai_generate_terms": True,
                "ai_generate_notes": True
            }

            # Process logo if provided
            logo_path = None
            if logo:
                logo_dir = Path(settings.UPLOAD_DIR) / "logos"
                logo_dir.mkdir(parents=True, exist_ok=True)
                logo_path = logo_dir / logo.filename

                content = await logo.read()
                with open(logo_path, "wb") as f:
                    f.write(content)

            # Create InvoiceRequest object
            invoice_request = InvoiceRequest(
                invoice_number=invoice_data["invoice_number"],
                client_name=invoice_data["client_name"],
                vendor_name=invoice_data["vendor_name"],
                client_address=invoice_data.get("client_address", ""),
                vendor_address=invoice_data.get("vendor_address", ""),
                line_items=invoice_data.get("line_items", []),
                currency=invoice_data.get("currency", "USD"),
                custom_terms=invoice_data.get("payment_terms", ""),
                custom_notes="",
                ai_generate_items=invoice_data.get("ai_generate_items", True),
                ai_generate_terms=invoice_data.get("ai_generate_terms", True),
                ai_generate_notes=invoice_data.get("ai_generate_notes", True),
                logo_path=str(logo_path) if logo_path else None,
                output_format="pdf"
            )

            # Generate invoice
            result = await invoice_use_case.execute(invoice_request)

            # Clean up temp files
            if logo_path:
                background_tasks.add_task(cleanup_temp_file, logo_path)

            # Format response to match frontend expectations
            return {
                "job_id": result.job_id,
                "status": result.status,
                "message": result.message,
                "download_url": result.download_url.replace("/invoice/", "/generate/"),
                "document_type": "invoice",
                "credits_used": 1
            }

        elif document_type == "infographic":
            # Placeholder for infographic generation
            return {
                "job_id": "INFOGRAPHIC-001",
                "status": "pending",
                "message": "Infographic generation coming soon",
                "document_type": "infographic"
            }

        elif document_type == "formal":
            # Placeholder for formal document generation
            return {
                "job_id": "FORMAL-001",
                "status": "pending",
                "message": "Formal document generation coming soon",
                "document_type": "formal"
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unknown document type: {document_type}")

    except Exception as e:
        logger.error(f"Document generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get generation job status.
    For now, returns completed for all jobs.
    """
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "message": "Document ready for download"
    }


@router.get("/download/{job_id}")
async def download_generated_document(job_id: str):
    """
    Download generated document by job ID.
    """
    try:
        # For invoices, job_id is the invoice number
        invoice_dir = Path(settings.PDF_OUTPUT_DIR) / "invoices"

        # Find matching files
        matching_files = list(invoice_dir.glob(f"*{job_id}*.pdf"))

        if not matching_files:
            # Try general documents directory
            doc_dir = Path(settings.PDF_OUTPUT_DIR)
            matching_files = list(doc_dir.glob(f"*{job_id}*.pdf"))

        if not matching_files:
            raise HTTPException(status_code=404, detail="Document not found")

        file_path = matching_files[0]

        return FileResponse(
            path=str(file_path),
            media_type="application/pdf",
            filename=file_path.name
        )

    except Exception as e:
        logger.error(f"Failed to download document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))