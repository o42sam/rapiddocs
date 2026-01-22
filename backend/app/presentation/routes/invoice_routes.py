"""
Invoice API Routes.
Handles HTTP requests for invoice generation and management.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import json
import logging

from ...application.use_cases.generate_invoice import GenerateInvoiceUseCase
from ...application.dto.invoice_request import InvoiceRequest
from ...application.dto.generation_response import GenerationResponse
from ...domain.interfaces.text_generator import ITextGenerator
from ...domain.interfaces.image_generator import IImageGenerator
from ...domain.interfaces.table_generator import ITableGenerator
from ...domain.interfaces.data_importer import IDataImporter
from ...infrastructure.document_renderers.invoice_pdf_renderer import InvoicePDFRenderer
from ...infrastructure.tables.reportlab_tables import ReportLabTableGenerator
from ...infrastructure.storage.file_storage import FileStorage
from ...infrastructure.persistence.mongodb_document_repository import MongoDBDocumentRepository
from ...infrastructure.ai_providers.huggingface_text_generator import HuggingFaceTextGenerator
from ...config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency injection functions
def get_text_generator() -> ITextGenerator:
    """Get text generator instance."""
    return HuggingFaceTextGenerator(
        api_key=settings.HUGGINGFACE_API_KEY,
        model=settings.TEXT_GENERATION_MODEL
    )


def get_image_generator() -> IImageGenerator:
    """Get image generator instance."""
    # Placeholder - implement when image generator is ready
    pass


def get_table_generator() -> ITableGenerator:
    """Get table generator instance."""
    return ReportLabTableGenerator()


def get_invoice_use_case(
    text_generator: ITextGenerator = Depends(get_text_generator),
    table_generator: ITableGenerator = Depends(get_table_generator)
) -> GenerateInvoiceUseCase:
    """Get invoice generation use case instance."""
    document_renderer = InvoicePDFRenderer(table_generator)
    document_repository = MongoDBDocumentRepository()

    return GenerateInvoiceUseCase(
        text_generator=text_generator,
        image_generator=None,  # Will be added when implemented
        table_generator=table_generator,
        document_renderer=document_renderer,
        document_repository=document_repository,
        data_importer=None  # Will be added when implemented
    )


@router.post("/generate", response_model=Dict[str, Any])
async def generate_invoice(
    background_tasks: BackgroundTasks,
    invoice_number: str = Form(...),
    client_name: str = Form(...),
    vendor_name: str = Form(...),
    description: str = Form(..., description="Description for AI content generation"),
    client_address: Optional[str] = Form(None),
    vendor_address: Optional[str] = Form(None),
    currency: Optional[str] = Form("USD"),
    payment_terms: Optional[str] = Form("Net 30"),
    line_items: Optional[str] = Form(None, description="JSON string of line items"),
    logo: Optional[UploadFile] = File(None),
    import_file: Optional[UploadFile] = File(None, description="CSV/Excel file with line items"),
    ai_generate_items: bool = Form(True, description="Generate line items from description"),
    ai_generate_terms: bool = Form(True, description="Generate payment terms using AI"),
    ai_generate_notes: bool = Form(True, description="Generate invoice notes using AI"),
    use_case: GenerateInvoiceUseCase = Depends(get_invoice_use_case)
):
    """
    Generate a professional invoice PDF.

    This endpoint accepts invoice details and optionally:
    - Generates line items from description using AI
    - Imports line items from CSV/Excel file
    - Processes company logo
    - Generates payment terms and notes using AI
    """
    try:
        # Process logo if provided
        logo_path = None
        if logo:
            # Save uploaded logo
            logo_dir = Path(settings.UPLOAD_DIR) / "logos"
            logo_dir.mkdir(parents=True, exist_ok=True)
            logo_path = logo_dir / logo.filename

            content = await logo.read()
            with open(logo_path, "wb") as f:
                f.write(content)

        # Process import file if provided
        import_path = None
        if import_file:
            # Save uploaded file
            import_dir = Path(settings.UPLOAD_DIR) / "imports"
            import_dir.mkdir(parents=True, exist_ok=True)
            import_path = import_dir / import_file.filename

            content = await import_file.read()
            with open(import_path, "wb") as f:
                f.write(content)

        # Parse line items if provided as JSON
        parsed_line_items = []
        if line_items and not import_file:
            try:
                items_data = json.loads(line_items)
                for item in items_data:
                    parsed_line_items.append({
                        "description": item.get("description", ""),
                        "quantity": int(item.get("quantity", 1)),
                        "unit_price": float(item.get("unit_price", 0)),
                        "tax_rate": float(item.get("tax_rate", 0))
                    })
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid line items JSON format")

        # Prepare invoice data
        invoice_data = {
            "invoice_number": invoice_number,
            "client_name": client_name,
            "client_address": client_address or "",
            "vendor_name": vendor_name,
            "vendor_address": vendor_address or "",
            "currency": currency,
            "payment_terms": payment_terms,
            "description": description,
            "line_items": parsed_line_items if parsed_line_items else [],
            "ai_generate_items": ai_generate_items and not parsed_line_items and not import_file,
            "ai_generate_terms": ai_generate_terms,
            "ai_generate_notes": ai_generate_notes
        }

        # Execute invoice generation
        result = await use_case.execute(
            invoice_data=invoice_data,
            logo_path=logo_path,
            import_file_path=import_path,
            output_dir=Path(settings.PDF_OUTPUT_DIR) / "invoices"
        )

        # Clean up temporary files in background
        if logo_path:
            background_tasks.add_task(cleanup_temp_file, logo_path)
        if import_path:
            background_tasks.add_task(cleanup_temp_file, import_path)

        return result

    except Exception as e:
        logger.error(f"Invoice generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{invoice_id}")
async def download_invoice(invoice_id: str):
    """
    Download a generated invoice PDF.

    Args:
        invoice_id: Invoice document ID

    Returns:
        PDF file response
    """
    try:
        # Construct file path
        invoice_dir = Path(settings.PDF_OUTPUT_DIR) / "invoices"

        # Find the invoice file (might have different naming patterns)
        matching_files = list(invoice_dir.glob(f"*{invoice_id}*.pdf"))

        if not matching_files:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Return the first matching file
        file_path = matching_files[0]

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Invoice file not found")

        return FileResponse(
            path=str(file_path),
            media_type="application/pdf",
            filename=file_path.name
        )

    except Exception as e:
        logger.error(f"Failed to download invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import-data")
async def import_invoice_data(
    file: UploadFile = File(..., description="CSV or Excel file with invoice data")
):
    """
    Import invoice line items from a CSV or Excel file.

    Expected columns:
    - description: Item description
    - quantity: Number of items
    - unit_price: Price per unit
    - tax_rate: Tax rate (optional)

    Returns:
        Parsed line items ready for invoice generation
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only CSV and Excel files are supported."
            )

        # Save temporary file
        temp_dir = Path("/tmp")
        temp_path = temp_dir / file.filename

        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        # Import data using appropriate importer
        if file.filename.endswith('.csv'):
            from ...infrastructure.data_import.csv_importer import CSVImporter
            importer = CSVImporter()
        else:
            from ...infrastructure.data_import.excel_importer import ExcelImporter
            importer = ExcelImporter()

        # Import and validate
        is_valid = await importer.validate_file(
            temp_path,
            expected_columns=["description", "quantity", "unit_price"]
        )

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Required columns: description, quantity, unit_price"
            )

        # Import data
        imported_data = await importer.import_file(temp_path)

        # Clean up
        temp_path.unlink()

        # Format response
        line_items = []
        for item in imported_data:
            line_items.append({
                "description": str(item.get("description", "")),
                "quantity": int(item.get("quantity", 1)),
                "unit_price": float(item.get("unit_price", 0)),
                "tax_rate": float(item.get("tax_rate", 0))
            })

        return {
            "success": True,
            "line_items": line_items,
            "count": len(line_items),
            "message": f"Successfully imported {len(line_items)} line items"
        }

    except Exception as e:
        logger.error(f"Data import failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_invoice_templates():
    """
    Get available invoice templates and sample data.

    Returns:
        List of template configurations and sample line items
    """
    return {
        "templates": [
            {
                "id": "professional",
                "name": "Professional Invoice",
                "description": "Clean, professional invoice template",
                "sample_data": {
                    "invoice_number": f"INV-{datetime.now().strftime('%Y%m')}-001",
                    "vendor_name": "Your Company Name",
                    "vendor_address": "123 Business Street\nCity, State 12345",
                    "client_name": "Client Company",
                    "client_address": "456 Client Avenue\nCity, State 67890",
                    "payment_terms": "Net 30",
                    "currency": "USD"
                },
                "sample_items": [
                    {
                        "description": "Professional Services",
                        "quantity": 10,
                        "unit_price": 150.00,
                        "tax_rate": 0.0
                    },
                    {
                        "description": "Consulting Hours",
                        "quantity": 5,
                        "unit_price": 200.00,
                        "tax_rate": 0.0
                    }
                ]
            },
            {
                "id": "detailed",
                "name": "Detailed Invoice",
                "description": "Invoice with detailed line items and tax",
                "sample_data": {
                    "invoice_number": f"INV-{datetime.now().strftime('%Y%m')}-002",
                    "payment_terms": "Due on receipt",
                    "currency": "USD"
                }
            }
        ]
    }


def cleanup_temp_file(file_path: Path):
    """
    Clean up temporary file.

    Args:
        file_path: Path to the file to delete
    """
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file {file_path}: {e}")