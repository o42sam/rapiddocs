"""
Generation API Routes.
Unified endpoint for all document generation types.
"""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any
from pathlib import Path
import json

# Import invoice use case (may fail if not yet implemented)
try:
    from ...application.use_cases.generate_invoice import GenerateInvoiceUseCase
    from ...application.dto.invoice_request import InvoiceRequest, InvoiceLineItemDTO
    from ...infrastructure.ai_providers.huggingface_text_generator import HuggingFaceTextGenerator
    from ...infrastructure.document_renderers.invoice_pdf_renderer import InvoicePDFRenderer
    from ...infrastructure.tables.reportlab_tables import ReportLabTableGenerator
    from ...infrastructure.persistence.mongodb_document_repository import MongoDBDocumentRepository
    from ...infrastructure.ai_providers.invoice_prompt_analyzer import InvoicePromptAnalyzer
    INVOICE_AVAILABLE = True
except ImportError:
    INVOICE_AVAILABLE = False

# Import infographic use case
from ...application.dto.infographic_request import InfographicRequest, StatisticDTO
from ...application.use_cases.generate_infographic import GenerateInfographicUseCase
from ...infrastructure.ai_providers.gemini_text_generator import GeminiTextGenerator
from ...infrastructure.ai_providers.banana_image_generator import BananaImageGenerator
from ...infrastructure.ai_providers.prompt_analyzer import PromptAnalyzer
from ...infrastructure.visualization.matplotlib_engine import MatplotlibEngine
from ...infrastructure.document_renderers.infographic_pdf_renderer import InfographicPDFRenderer
from ...infrastructure.document_renderers.infographic_styles import get_style_preset
from ...infrastructure.data_import.csv_importer import CSVImporter

from ...config import settings
from ...shared.logger import get_logger

logger = get_logger("generation_routes")

# In-memory job storage (replace with database in production)
_job_storage = {}

router = APIRouter(prefix="/generate", tags=["Document Generation"])


# Dependency injection functions for infographic generation
def get_text_generator() -> GeminiTextGenerator:
    """Dependency for text generator."""
    return GeminiTextGenerator(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL
    )


def get_image_generator() -> BananaImageGenerator:
    """Dependency for image generator."""
    return BananaImageGenerator(
        api_key=settings.HUGGINGFACE_API_KEY,
        model=settings.IMAGE_GENERATION_MODEL
    )


def get_visualization_engine() -> MatplotlibEngine:
    """Dependency for visualization engine."""
    return MatplotlibEngine()


def get_document_renderer() -> InfographicPDFRenderer:
    """Dependency for document renderer."""
    return InfographicPDFRenderer()


def get_prompt_analyzer(
    text_generator: GeminiTextGenerator = Depends(get_text_generator)
) -> PromptAnalyzer:
    """Dependency for prompt analyzer."""
    return PromptAnalyzer(text_generator)


def get_csv_importer() -> CSVImporter:
    """Dependency for CSV importer."""
    return CSVImporter()


def get_infographic_use_case(
    text_generator: GeminiTextGenerator = Depends(get_text_generator),
    image_generator: BananaImageGenerator = Depends(get_image_generator),
    visualization_engine: MatplotlibEngine = Depends(get_visualization_engine),
    document_renderer: InfographicPDFRenderer = Depends(get_document_renderer),
    prompt_analyzer: PromptAnalyzer = Depends(get_prompt_analyzer),
    csv_importer: CSVImporter = Depends(get_csv_importer)
) -> GenerateInfographicUseCase:
    """Dependency for the infographic generation use case."""
    return GenerateInfographicUseCase(
        text_generator=text_generator,
        image_generator=image_generator,
        visualization_engine=visualization_engine,
        document_renderer=document_renderer,
        prompt_analyzer=prompt_analyzer,
        data_importer=csv_importer
    )


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
    infographic_use_case: GenerateInfographicUseCase = Depends(get_infographic_use_case)
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
            if not INVOICE_AVAILABLE:
                raise HTTPException(
                    status_code=501,
                    detail="Invoice generation not yet implemented"
                )

            # Build invoice use case
            inv_text_gen = HuggingFaceTextGenerator(
                api_key=settings.HUGGINGFACE_API_KEY,
                model=settings.TEXT_GENERATION_MODEL
            )
            inv_table_gen = ReportLabTableGenerator()
            inv_renderer = InvoicePDFRenderer(inv_table_gen)
            inv_repo = MongoDBDocumentRepository()
            invoice_use_case = GenerateInvoiceUseCase(
                text_generator=inv_text_gen,
                image_generator=None,
                document_renderer=inv_renderer,
                table_generator=inv_table_gen,
                document_repository=inv_repo,
            )
            job_id = str(uuid.uuid4())[:8]
            logger.info(f"Processing invoice generation - Job ID: {job_id}")

            _job_storage[job_id] = {
                "status": "processing",
                "progress": 0,
                "message": "Starting invoice generation..."
            }

            # Use AI to extract invoice data from the user's prompt
            gemini_gen = GeminiTextGenerator(
                api_key=settings.GEMINI_API_KEY,
                model=settings.GEMINI_MODEL
            )
            invoice_analyzer = InvoicePromptAnalyzer(gemini_gen)
            extracted = await invoice_analyzer.analyze(description)
            logger.info(f"AI extracted invoice data: vendor={extracted.vendor_name}, client={extracted.client_name}, items={len(extracted.line_items)}")

            # Process logo if provided
            logo_path = None
            if logo:
                logo_dir = Path(settings.UPLOAD_DIR) / "logos"
                logo_dir.mkdir(parents=True, exist_ok=True)
                logo_path = logo_dir / f"{job_id}_{logo.filename}"
                content = await logo.read()
                with open(logo_path, "wb") as f:
                    f.write(content)

            # Build line item DTOs: design_spec overrides take priority, then AI-extracted
            line_item_dtos = []
            if design.get("line_items"):
                for item in design["line_items"]:
                    if isinstance(item, dict):
                        line_item_dtos.append(InvoiceLineItemDTO(
                            description=item.get("description", ""),
                            quantity=int(item.get("quantity", 1)),
                            unit_price=float(item.get("unit_price", 0)),
                            tax_rate=float(item.get("tax_rate", 0))
                        ))

            # Use AI-extracted line items if none provided via design_spec
            if not line_item_dtos:
                for item in extracted.line_items:
                    line_item_dtos.append(InvoiceLineItemDTO(
                        description=item.description,
                        quantity=int(item.quantity),
                        unit_price=item.unit_price,
                        tax_rate=item.tax_rate
                    ))

            # Build InvoiceRequest DTO - design_spec fields override AI-extracted values
            # Only use AI generation for terms/notes if we don't have real extracted data
            custom_terms = design.get("payment_terms") or extracted.payment_terms
            custom_notes = design.get("notes") or extracted.notes
            invoice_request = InvoiceRequest(
                invoice_number=f"INV-{job_id.upper()}",
                client_name=design.get("client_name") or extracted.client_name,
                client_address=design.get("client_address") or extracted.client_address,
                vendor_name=design.get("vendor_name") or extracted.vendor_name,
                vendor_address=design.get("vendor_address") or extracted.vendor_address,
                line_items=line_item_dtos,
                currency=design.get("currency") or extracted.currency,
                logo_path=str(logo_path) if logo_path else None,
                ai_generate_terms=not bool(custom_terms),
                ai_generate_notes=not bool(custom_notes),
                custom_terms=custom_terms,
                custom_notes=custom_notes,
            )

            try:
                result = await invoice_use_case.execute(invoice_request)

                # The use case writes to /tmp/invoice_{document_id}.pdf
                invoice_file = Path(f"/tmp/invoice_{result.document_id}.pdf")
                _job_storage[job_id] = {
                    "status": "completed",
                    "progress": 100,
                    "message": "Generation complete",
                    "file_path": str(invoice_file)
                }

                return {
                    "job_id": job_id,
                    "status": "completed",
                    "message": "Invoice document generated successfully",
                    "download_url": f"{settings.API_PREFIX}/generate/download/{job_id}",
                    "document_type": "invoice",
                    "credits_used": 1
                }
            except Exception as e:
                _job_storage[job_id] = {
                    "status": "failed",
                    "progress": 0,
                    "message": str(e),
                    "error": str(e)
                }
                raise

        elif document_type == "infographic":
            # Process infographic generation
            job_id = str(uuid.uuid4())[:8]
            logger.info(f"Processing infographic generation - Job ID: {job_id}")

            # Convert statistics to DTOs
            stat_dtos = []
            for stat in stats:
                if isinstance(stat, dict):
                    stat_dtos.append(StatisticDTO(
                        name=stat.get("name", "Statistic"),
                        value=float(stat.get("value", 0)),
                        unit=stat.get("unit", "units"),
                        visualization_type=stat.get("visualization_type", "bar_chart"),
                        category=stat.get("category"),
                        description=stat.get("description")
                    ))

            # Extract color scheme from design spec and convert to hex colors
            color_scheme_name = "professional"
            if design:
                primary_color = design.get("primary_color", "").lower()
                if "green" in primary_color:
                    color_scheme_name = "nature"
                elif "purple" in primary_color:
                    color_scheme_name = "modern"
                elif "orange" in primary_color or "red" in primary_color:
                    color_scheme_name = "warm"
                elif "blue" in primary_color:
                    color_scheme_name = "corporate"

            # Convert color scheme name to hex colors using style presets
            style_preset = get_style_preset(color_scheme_name)
            color_scheme = [
                style_preset.colors.primary,
                style_preset.colors.secondary,
                style_preset.colors.tertiary,
                style_preset.colors.accent
            ]

            # Process logo if provided
            logo_path = None
            if logo:
                logo_dir = Path(settings.UPLOAD_DIR) / "logos"
                logo_dir.mkdir(parents=True, exist_ok=True)
                logo_path = logo_dir / f"{job_id}_{logo.filename}"
                content = await logo.read()
                with open(logo_path, "wb") as f:
                    f.write(content)
                logo_path = str(logo_path)

            # Create infographic request DTO
            dto = InfographicRequest(
                title="",  # Will be extracted from prompt
                topic=description,
                statistics=stat_dtos,
                num_sections=max(3, length // 200),  # Estimate sections from length
                num_images=max(2, length // 300),    # Estimate images from length
                color_scheme=color_scheme,
                logo_path=logo_path,
                output_format="pdf",
                include_cover_page=True
            )

            # Store job status
            _job_storage[job_id] = {
                "status": "processing",
                "progress": 0,
                "message": "Starting infographic generation..."
            }

            try:
                # Execute generation
                output_path = await infographic_use_case.execute(dto)

                # Update job status
                _job_storage[job_id] = {
                    "status": "completed",
                    "progress": 100,
                    "message": "Generation complete",
                    "file_path": str(output_path)
                }

                return {
                    "job_id": job_id,
                    "status": "completed",
                    "message": "Infographic document generated successfully",
                    "download_url": f"{settings.API_PREFIX}/generate/download/{job_id}",
                    "document_type": "infographic",
                    "credits_used": 1
                }

            except Exception as e:
                _job_storage[job_id] = {
                    "status": "failed",
                    "progress": 0,
                    "message": str(e),
                    "error": str(e)
                }
                raise

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
    Checks in-memory job storage first, then returns default completed status.
    """
    if job_id in _job_storage:
        job = _job_storage[job_id]
        return {
            "job_id": job_id,
            "status": job.get("status", "unknown"),
            "progress": job.get("progress", 0),
            "message": job.get("message"),
            "file_path": job.get("file_path"),
            "error": job.get("error")
        }

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
        # Check job storage first
        if job_id in _job_storage:
            job = _job_storage[job_id]
            if job.get("status") != "completed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Job not completed. Status: {job.get('status')}"
                )
            file_path = job.get("file_path")
            if file_path and Path(file_path).exists():
                return FileResponse(
                    path=file_path,
                    media_type="application/pdf",
                    filename=Path(file_path).name
                )

        # Fallback: search in PDF output directories
        # Try infographic directory first
        doc_dir = Path(settings.PDF_OUTPUT_DIR)
        matching_files = list(doc_dir.glob(f"*{job_id}*.pdf"))

        if not matching_files:
            # Try invoices subdirectory
            invoice_dir = doc_dir / "invoices"
            if invoice_dir.exists():
                matching_files = list(invoice_dir.glob(f"*{job_id}*.pdf"))

        if not matching_files:
            raise HTTPException(status_code=404, detail="Document not found")

        file_path = matching_files[0]

        return FileResponse(
            path=str(file_path),
            media_type="application/pdf",
            filename=file_path.name
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))