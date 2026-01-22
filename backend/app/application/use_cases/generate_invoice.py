"""
Invoice Generation Use Case.
Orchestrates the generation of invoice documents.
"""

from typing import Optional
from pathlib import Path
from decimal import Decimal
import logging

from ..dto.invoice_request import InvoiceRequest
from ..dto.generation_response import GenerationResponse
from ...domain.interfaces.text_generator import ITextGenerator
from ...domain.interfaces.image_generator import IImageGenerator
from ...domain.interfaces.document_renderer import IDocumentRenderer
from ...domain.interfaces.table_generator import ITableGenerator
from ...domain.interfaces.data_importer import IDataImporter
from ...domain.interfaces.document_repository import IDocumentRepository
from ...domain.entities.document import Document, DocumentType
from ...domain.entities.invoice import Invoice, LineItem
from ...domain.entities.generation_job import GenerationJob
from ...domain.exceptions import GenerationException, ValidationException

logger = logging.getLogger(__name__)


class GenerateInvoiceUseCase:
    """
    Use case for generating invoice documents.

    Components:
    - Text Generator: Generates invoice descriptions, notes, terms
    - Image Generator: Generates/processes business logo
    - Table Generator: Creates line items and summary tables
    - Document Renderer: Outputs final document in specified format
    - Data Importer: (Optional) Imports line items from CSV/Excel
    - Document Repository: Stores document metadata
    """

    def __init__(
        self,
        text_generator: ITextGenerator,
        image_generator: IImageGenerator,
        document_renderer: IDocumentRenderer,
        table_generator: ITableGenerator,
        document_repository: IDocumentRepository,
        data_importer: Optional[IDataImporter] = None
    ):
        self._text_generator = text_generator
        self._image_generator = image_generator
        self._document_renderer = document_renderer
        self._table_generator = table_generator
        self._document_repository = document_repository
        self._data_importer = data_importer

    async def execute(self, request: InvoiceRequest) -> GenerationResponse:
        """
        Execute invoice generation.

        Args:
            request: Invoice generation request

        Returns:
            Generation response with document and job IDs
        """
        # Validate request
        errors = request.validate()
        if errors:
            raise ValidationException("Invalid invoice request", {"errors": errors})

        # Create document entity
        document = Document(
            type=DocumentType.INVOICE,
            user_id=request.user_id or "anonymous",
            title=f"Invoice {request.invoice_number}"
        )

        # Create generation job
        job = GenerationJob(
            document_id=document.id,
            user_id=document.user_id,
            job_type="invoice_generation"
        )

        try:
            # Mark as processing
            document.mark_processing()
            job.start()

            # Import line items if file provided
            line_items = request.line_items
            if request.import_file_path and self._data_importer:
                imported_data = await self._data_importer.import_file(
                    Path(request.import_file_path)
                )
                line_items = self._convert_imported_to_line_items(imported_data)

            # Create invoice entity
            invoice = Invoice(
                invoice_number=request.invoice_number,
                client_name=request.client_name,
                client_address=request.client_address,
                vendor_name=request.vendor_name,
                vendor_address=request.vendor_address,
                line_items=[],
                currency=request.currency
            )

            # Add line items
            for item in line_items:
                invoice.add_line_item(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=Decimal(str(item.unit_price)),
                    tax_rate=Decimal(str(item.tax_rate))
                )

            # Generate AI content if requested
            payment_terms = request.custom_terms
            notes = request.custom_notes

            if request.ai_generate_terms:
                payment_terms = await self._generate_payment_terms(invoice)

            if request.ai_generate_notes:
                notes = await self._generate_invoice_notes(invoice)

            # Set terms and notes
            invoice.payment_terms = payment_terms
            invoice.notes = notes

            # Create invoice table
            items_table = self._table_generator.create_invoice_table(
                line_items=[item.to_dict() for item in invoice.line_items],
                columns=["Description", "Quantity", "Unit Price", "Tax", "Total"]
            )

            # Create summary table
            summary_table = self._table_generator.create_summary_table(
                subtotal=float(invoice.subtotal),
                tax=float(invoice.total_tax),
                total=float(invoice.total),
                currency=invoice.currency
            )

            # Prepare document content
            content = {
                "invoice": invoice.to_dict(),
                "items_table": items_table,
                "summary_table": summary_table,
                "logo_path": request.logo_path,
                "color_scheme": request.color_scheme
            }

            # Render document
            output_path = Path(f"/tmp/invoice_{document.id}.{request.output_format}")
            rendered_path = await self._document_renderer.render(
                content=content,
                output_path=output_path,
                format=request.output_format
            )

            # Mark as completed
            document.mark_completed(str(rendered_path))
            job.complete({"path": str(rendered_path)})

            # Save to repository
            await self._document_repository.save_document(
                document_id=document.id,
                document_data=document.to_dict(),
                user_id=document.user_id
            )

            # Return response
            return GenerationResponse(
                document_id=document.id,
                job_id=job.id,
                status="completed",
                message="Invoice generated successfully",
                download_url=f"/api/v1/invoice/download/{document.id}",
                created_at=document.created_at
            )

        except Exception as e:
            logger.error(f"Invoice generation failed: {str(e)}")
            document.mark_failed(str(e))
            job.fail(str(e))

            await self._document_repository.update_document_status(
                document_id=document.id,
                status="failed",
                error_message=str(e)
            )

            raise GenerationException(f"Invoice generation failed: {str(e)}")

    async def _generate_payment_terms(self, invoice: Invoice) -> str:
        """Generate payment terms using AI."""
        prompt = f"""
        Generate professional payment terms for an invoice with the following details:
        - Invoice Number: {invoice.invoice_number}
        - Total Amount: {invoice.currency} {invoice.total}
        - Due Date: {invoice.due_date}

        Generate concise, professional payment terms (2-3 sentences).
        """

        return await self._text_generator.generate(
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )

    async def _generate_invoice_notes(self, invoice: Invoice) -> str:
        """Generate invoice notes using AI."""
        prompt = f"""
        Generate professional invoice notes for a business invoice.
        The invoice is for {invoice.client_name} from {invoice.vendor_name}.
        Total amount: {invoice.currency} {invoice.total}

        Generate brief, professional notes (2-3 sentences) thanking the client
        and providing contact information for questions.
        """

        return await self._text_generator.generate(
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )

    def _convert_imported_to_line_items(self, imported_data: list) -> list:
        """Convert imported data to line items."""
        line_items = []
        for row in imported_data:
            # Expected columns: item, description, quantity, unit_price, tax_rate
            line_items.append({
                "description": row.get("description", row.get("item", "")),
                "quantity": int(row.get("quantity", 1)),
                "unit_price": float(row.get("unit_price", 0)),
                "tax_rate": float(row.get("tax_rate", 0))
            })
        return line_items