"""
Simple invoice PDF generator using ReportLab
Generates clean invoices with centered logo, header text, and borderless items table
"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER
from typing import Optional
import os

from app.schemas.invoice import InvoiceData
from app.models.document import DesignSpecification
from app.utils.logger import get_logger
from app.utils.exceptions import PDFGenerationError

logger = get_logger('invoice_pdf_reportlab')


class ReportLabInvoicePDFGenerator:
    """Generate simple invoice PDFs with centered logo, header, and items table"""

    def __init__(self):
        # Letter paper size: 8.5" x 11"
        self.page_width = 8.5 * inch
        self.page_height = 11 * inch

        # Standard margins
        self.margin = 0.75 * inch

    def _hex_to_reportlab_color(self, hex_color: str):
        """Convert hex color to ReportLab Color object"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return colors.Color(r, g, b)

    def generate_invoice_pdf(
        self,
        output_path: str,
        invoice_data: InvoiceData,
        design_spec: DesignSpecification,
        logo_path: Optional[str] = None,
        use_watermark: bool = False
    ) -> str:
        """
        Generate a simple invoice PDF with centered logo, header, and items table

        Args:
            output_path: Path where the PDF will be saved
            invoice_data: Complete invoice data
            design_spec: Design specifications (colors)
            logo_path: Optional company logo
            use_watermark: Not used (kept for API compatibility)

        Returns:
            Path to generated PDF
        """
        try:
            logger.info(f"Generating simple invoice PDF: {invoice_data.invoice_number}")

            # Create PDF document with letter size
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )

            # Build document content
            flowables = []

            # 1. Add centered logo
            if logo_path and os.path.exists(logo_path):
                try:
                    # Calculate proportional logo dimensions (max 2" wide, 1.5" tall)
                    ir = ImageReader(logo_path)
                    iw, ih = ir.getSize()
                    aspect = ih / float(iw)
                    logo_width = min(2.0 * inch, iw)
                    logo_height = logo_width * aspect

                    # Limit height
                    if logo_height > 1.5 * inch:
                        logo_height = 1.5 * inch
                        logo_width = logo_height / aspect

                    logo_img = Image(logo_path, width=logo_width, height=logo_height)
                    logo_img.hAlign = 'CENTER'
                    flowables.append(logo_img)
                    flowables.append(Spacer(1, 0.3 * inch))

                    logger.info(f"Logo added: {logo_width:.2f}\" x {logo_height:.2f}\"")
                except Exception as e:
                    logger.warning(f"Failed to load logo: {str(e)}")

            # 2. Add centered header text
            styles = getSampleStyleSheet()
            header_style = ParagraphStyle(
                'InvoiceHeader',
                parent=styles['Normal'],
                fontSize=14,
                alignment=TA_CENTER,
                spaceAfter=20
            )

            # Create header text with invoice info
            header_text = f"<b>Invoice #{invoice_data.invoice_number}</b><br/>"
            header_text += f"From: {invoice_data.bill_from_name}<br/>"
            header_text += f"To: {invoice_data.bill_to_name}<br/>"
            header_text += f"Date: {invoice_data.invoice_date} | Due: {invoice_data.due_date}"

            flowables.append(Paragraph(header_text, header_style))
            flowables.append(Spacer(1, 0.3 * inch))

            # 3. Add borderless items table
            flowables.append(self._build_items_table(invoice_data))

            # Build the PDF
            doc.build(flowables)

            logger.info(f"Invoice PDF generated successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate invoice PDF: {str(e)}", exc_info=True)
            raise PDFGenerationError(
                f"Failed to generate invoice PDF: {str(e)}",
                details={'output_path': output_path, 'invoice_number': invoice_data.invoice_number}
            )

    def _build_items_table(self, invoice_data: InvoiceData) -> Table:
        """Build simple borderless items table with Item, Quantity, Price columns"""
        styles = getSampleStyleSheet()

        # Prepare table data
        data = []

        # Header row
        header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )

        data.append([
            Paragraph("<b>Item</b>", header_style),
            Paragraph("<b>Quantity</b>", header_style),
            Paragraph("<b>Price</b>", header_style)
        ])

        # Data rows
        row_style = ParagraphStyle(
            'TableRow',
            parent=styles['Normal'],
            fontSize=11
        )

        for item in invoice_data.line_items:
            # Format quantity
            qty_str = f"{item.quantity:.0f}" if item.quantity == int(item.quantity) else f"{item.quantity:.2f}"

            data.append([
                Paragraph(item.description, row_style),
                Paragraph(qty_str, row_style),
                Paragraph(f"${item.amount:,.2f}", row_style)
            ])

        # Create table with appropriate column widths (letter size is 8.5", minus 1.5" margins = 7")
        col_widths = [4.0 * inch, 1.5 * inch, 1.5 * inch]
        table = Table(data, colWidths=col_widths)

        # Table styling - borderless with simple lines between rows
        table_style = [
            # Header row styling
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # Content alignment
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Item column
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),    # Quantity column
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),     # Price column

            # Content padding
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),

            # No borders - completely borderless
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
            ('LINEBELOW', (0, 0), (-1, -1), 0, colors.white),
        ]

        table.setStyle(TableStyle(table_style))
        table.hAlign = 'CENTER'

        return table


# Singleton instance
reportlab_invoice_pdf_generator = ReportLabInvoicePDFGenerator()


# Convenience function
def generate_invoice_pdf(
    output_path: str,
    invoice_data: InvoiceData,
    design_spec: DesignSpecification,
    logo_path: Optional[str] = None,
    use_watermark: bool = False
) -> str:
    """Convenience function to generate invoice PDF using ReportLab"""
    return reportlab_invoice_pdf_generator.generate_invoice_pdf(
        output_path,
        invoice_data,
        design_spec,
        logo_path,
        use_watermark
    )
