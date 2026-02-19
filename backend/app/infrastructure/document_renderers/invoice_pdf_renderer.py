"""
Invoice PDF Renderer Implementation.
Generates professional invoice PDFs using ReportLab.
Based on the provided template design.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import os
import math

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from PIL import Image

from ...domain.entities.invoice import Invoice, LineItem
from ..tables.reportlab_tables import ReportLabTableGenerator


class InvoicePDFRenderer:
    """
    Renders invoices to PDF format using ReportLab.
    Creates professional-looking invoices with all required elements.
    """

    def __init__(self, table_generator: Optional[ReportLabTableGenerator] = None):
        """
        Initialize the invoice PDF renderer.

        Args:
            table_generator: Optional table generator, creates default if not provided
        """
        self.table_generator = table_generator or ReportLabTableGenerator()
        self.colors = self._init_colors()

    def _init_colors(self) -> Dict[str, Any]:
        """Initialize color palette for the invoice."""
        return {
            "header_bg": colors.Color(0.95, 0.95, 0.95),  # Light gray
            "dark_text": colors.Color(0.2, 0.2, 0.2),
            "accent": colors.Color(0.3, 0.3, 0.3),
            "light_gray": colors.Color(0.6, 0.6, 0.6),
            "table_header": colors.Color(0.25, 0.25, 0.25),
            "table_alt_row": colors.Color(0.97, 0.97, 0.97),
            "border": colors.Color(0.85, 0.85, 0.85)
        }

    async def render(self, content: Dict[str, Any], output_path: Path, format: str = "pdf") -> Path:
        """
        Render invoice document (IDocumentRenderer-compatible interface).

        Args:
            content: Dict with 'invoice' (Invoice entity or dict), 'logo_path', etc.
            output_path: Path where the PDF will be saved
            format: Output format (only 'pdf' supported)

        Returns:
            Path to the generated PDF
        """
        invoice_data = content.get("invoice")
        # If it's a dict (from to_dict()), reconstruct the Invoice entity
        if isinstance(invoice_data, dict):
            from ...domain.entities.invoice import Invoice, LineItem
            from decimal import Decimal
            invoice = Invoice(
                invoice_number=invoice_data.get("invoice_number", ""),
                client_name=invoice_data.get("client_name", ""),
                client_address=invoice_data.get("client_address", ""),
                vendor_name=invoice_data.get("vendor_name", ""),
                vendor_address=invoice_data.get("vendor_address", ""),
                line_items=[],
                currency=invoice_data.get("currency", "USD"),
            )
            for item in invoice_data.get("line_items", []):
                invoice.add_line_item(
                    description=item.get("description", ""),
                    quantity=item.get("quantity", 1),
                    unit_price=Decimal(str(item.get("unit_price", 0))),
                    tax_rate=Decimal(str(item.get("tax_rate", 0))),
                )
            if invoice_data.get("payment_terms"):
                invoice.payment_terms = invoice_data["payment_terms"]
            if invoice_data.get("notes"):
                invoice.notes = invoice_data["notes"]
        else:
            invoice = invoice_data

        logo_path = content.get("logo_path")
        if logo_path:
            logo_path = Path(logo_path)
        ai_content = content.get("ai_generated_content")
        return self.render_invoice(invoice, output_path, logo_path, ai_content)

    def render_invoice(
        self,
        invoice: Invoice,
        output_path: Path,
        logo_path: Optional[Path] = None,
        ai_generated_content: Optional[Dict[str, str]] = None
    ) -> Path:
        """
        Render an invoice to PDF.

        Args:
            invoice: Invoice entity to render
            output_path: Path where the PDF will be saved
            logo_path: Optional path to company logo image
            ai_generated_content: Optional AI-generated content for various sections

        Returns:
            Path to the generated PDF
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create canvas
        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter

        # Set margins
        left_margin = 50
        right_margin = width - 50
        top_margin = height - 50

        # Draw invoice components
        current_y = top_margin

        # Header section
        current_y = self._draw_header(
            c, invoice, logo_path, left_margin, right_margin, current_y
        )

        # Invoice details section
        current_y = self._draw_invoice_details(
            c, invoice, left_margin, right_margin, current_y - 30
        )

        # Items table
        current_y = self._draw_items_table(
            c, invoice, left_margin, right_margin, current_y - 30
        )

        # Summary section
        current_y = self._draw_summary(
            c, invoice, left_margin, right_margin, current_y - 20
        )

        # Payment info section
        current_y = self._draw_payment_info(
            c, invoice, ai_generated_content, left_margin, right_margin, current_y - 40
        )

        # Terms and conditions
        current_y = self._draw_terms_and_conditions(
            c, invoice, ai_generated_content, left_margin, right_margin, current_y - 30
        )

        # Signature section
        self._draw_signature_section(
            c, right_margin - 150, right_margin, current_y - 30
        )

        # Save the PDF
        c.save()

        return output_path

    def _draw_header(
        self,
        c: canvas.Canvas,
        invoice: Invoice,
        logo_path: Optional[Path],
        left_margin: float,
        right_margin: float,
        top_y: float
    ) -> float:
        """Draw the header section with logo and company info."""
        logo_size = 40
        logo_x = left_margin
        logo_y = top_y - 40

        # Draw logo or placeholder
        if logo_path and logo_path.exists():
            try:
                # Get image dimensions to maintain aspect ratio
                img = Image.open(logo_path)
                img_width, img_height = img.size
                aspect_ratio = img_width / img_height

                # Adjust dimensions to fit within logo_size
                if aspect_ratio > 1:
                    # Wider than tall
                    display_width = logo_size
                    display_height = logo_size / aspect_ratio
                else:
                    # Taller than wide
                    display_height = logo_size
                    display_width = logo_size * aspect_ratio

                c.drawImage(
                    str(logo_path),
                    logo_x,
                    logo_y - 10,
                    width=display_width,
                    height=display_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception as e:
                print(f"Error loading logo: {e}")
                self._draw_logo_placeholder(c, logo_x, logo_y, logo_size)
        else:
            self._draw_logo_placeholder(c, logo_x, logo_y, logo_size)

        # Business name
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(self.colors["dark_text"])
        c.drawString(logo_x + logo_size + 10, logo_y + 15, invoice.vendor_name)

        # Business tagline or address
        if invoice.vendor_address:
            lines = invoice.vendor_address.split('\n')
            c.setFont("Helvetica", 8)
            c.setFillColor(self.colors["light_gray"])
            y_offset = 0
            for line in lines[:2]:  # Show max 2 lines
                c.drawString(logo_x + logo_size + 10, logo_y - y_offset, line.strip())
                y_offset += 12

        # "INVOICE" title
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(self.colors["dark_text"])
        c.drawRightString(right_margin, top_y - 30, "INVOICE")

        return top_y - 80

    def _draw_invoice_details(
        self,
        c: canvas.Canvas,
        invoice: Invoice,
        left_margin: float,
        right_margin: float,
        start_y: float
    ) -> float:
        """Draw invoice details section."""
        # Invoice to section
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(self.colors["dark_text"])
        c.drawString(left_margin, start_y, "Invoice to:")

        # Customer name
        c.setFont("Helvetica", 10)
        c.drawString(left_margin, start_y - 15, invoice.client_name)

        # Customer address
        if invoice.client_address:
            c.setFillColor(self.colors["light_gray"])
            address_lines = invoice.client_address.split('\n')
            y_offset = 30
            for line in address_lines[:3]:  # Max 3 lines
                c.drawString(left_margin, start_y - y_offset, line.strip())
                y_offset += 15

        # Invoice number and date on the right
        label_x = right_margin - 120
        c.setFont("Helvetica", 10)
        c.setFillColor(self.colors["dark_text"])

        c.drawString(label_x, start_y, "Invoice#")
        c.drawRightString(right_margin, start_y, invoice.invoice_number)

        c.drawString(label_x, start_y - 18, "Date")
        date_str = invoice.issue_date.strftime("%d/%m/%Y")
        c.drawRightString(right_margin, start_y - 18, date_str)

        if invoice.due_date:
            c.drawString(label_x, start_y - 36, "Due Date")
            due_date_str = invoice.due_date.strftime("%d/%m/%Y")
            c.drawRightString(right_margin, start_y - 36, due_date_str)

        return start_y - 80

    def _draw_items_table(
        self,
        c: canvas.Canvas,
        invoice: Invoice,
        left_margin: float,
        right_margin: float,
        start_y: float
    ) -> float:
        """Draw the items table."""
        # Prepare line items data
        line_items_data = []
        for item in invoice.line_items:
            line_items_data.append({
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "total": float(item.total)
            })

        # Create table using table generator
        columns = ["SL.", "Item Description", "Price", "Qty.", "Total"]
        table = self.table_generator.create_invoice_table(
            line_items_data,
            columns
        )

        # Calculate table position
        table_width, table_height = table.wrap(0, 0)

        # Draw the table
        table.drawOn(c, left_margin, start_y - table_height)

        return start_y - table_height

    def _draw_summary(
        self,
        c: canvas.Canvas,
        invoice: Invoice,
        left_margin: float,
        right_margin: float,
        start_y: float
    ) -> float:
        """Draw the summary section with totals."""
        # Thank you message on the left
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(self.colors["light_gray"])
        c.drawString(left_margin, start_y, "Thank you for your business")

        # Summary table on the right
        subtotal = float(invoice.subtotal)
        tax = float(invoice.total_tax)
        total = float(invoice.total)

        # Draw totals
        totals_label_x = right_margin - 120
        c.setFont("Helvetica", 10)
        c.setFillColor(self.colors["dark_text"])

        c.drawString(totals_label_x, start_y, "Sub Total:")
        c.drawRightString(right_margin, start_y, f"${subtotal:.2f}")

        if tax > 0:
            c.drawString(totals_label_x, start_y - 18, "Tax:")
            c.drawRightString(right_margin, start_y - 18, f"${tax:.2f}")

        # Total with bold font
        c.setFont("Helvetica-Bold", 12)
        c.drawString(totals_label_x, start_y - 45, "Total:")
        c.drawRightString(right_margin, start_y - 45, f"${total:.2f}")

        return start_y - 60

    def _draw_payment_info(
        self,
        c: canvas.Canvas,
        invoice: Invoice,
        ai_content: Optional[Dict[str, str]],
        left_margin: float,
        right_margin: float,
        start_y: float
    ) -> float:
        """Draw payment information section."""
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(self.colors["dark_text"])
        c.drawString(left_margin, start_y, "Payment Info:")

        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors["light_gray"])

        info_y = start_y - 18

        # Use AI-generated payment instructions if available
        payment_text = ""
        if ai_content and "payment_instructions" in ai_content:
            payment_text = ai_content["payment_instructions"]
        elif getattr(invoice, 'payment_instructions', None) or invoice.payment_terms:
            payment_text = getattr(invoice, 'payment_instructions', None) or invoice.payment_terms

        if payment_text:
            # Word wrap payment instructions
            lines = self._word_wrap(payment_text, 60)
            for line in lines[:3]:  # Max 3 lines
                c.drawString(left_margin, info_y, line)
                info_y -= 15
        else:
            # Default payment info
            bank_account_number = getattr(invoice, 'bank_account_number', None)
            if bank_account_number:
                c.drawString(left_margin, info_y, f"Account #:    {bank_account_number}")
                info_y -= 15
            bank_account_name = getattr(invoice, 'bank_account_name', None)
            if bank_account_name:
                c.drawString(left_margin, info_y, f"A/C Name:     {bank_account_name}")
                info_y -= 15
            bank_details = getattr(invoice, 'bank_details', None)
            if bank_details:
                c.drawString(left_margin, info_y, f"Bank Details:  {bank_details}")
                info_y -= 15

        return start_y - 70

    def _draw_terms_and_conditions(
        self,
        c: canvas.Canvas,
        invoice: Invoice,
        ai_content: Optional[Dict[str, str]],
        left_margin: float,
        right_margin: float,
        start_y: float
    ) -> float:
        """Draw terms and conditions section."""
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(self.colors["dark_text"])
        c.drawString(left_margin, start_y, "Terms & Conditions")

        c.setFont("Helvetica", 8)
        c.setFillColor(self.colors["light_gray"])

        # Use AI-generated terms if available
        terms_text = ""
        if ai_content and "terms_and_conditions" in ai_content:
            terms_text = ai_content["terms_and_conditions"]
        elif getattr(invoice, 'terms_and_conditions', None):
            terms_text = invoice.terms_and_conditions
        elif invoice.payment_terms:
            terms_text = invoice.payment_terms
        else:
            terms_text = "Payment is due within the specified timeframe. Late payments may incur additional charges."

        # Word wrap and draw terms
        lines = self._word_wrap(terms_text, 70)
        line_y = start_y - 18
        for line in lines[:4]:  # Max 4 lines
            c.drawString(left_margin, line_y, line)
            line_y -= 12

        return start_y - 70

    def _draw_signature_section(
        self,
        c: canvas.Canvas,
        sig_x: float,
        right_margin: float,
        sig_y: float
    ) -> None:
        """Draw the signature section."""
        # Signature line
        c.setStrokeColor(self.colors["light_gray"])
        c.setLineWidth(0.5)
        c.line(sig_x, sig_y, right_margin, sig_y)

        # Label
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors["dark_text"])
        c.drawCentredString((sig_x + right_margin) / 2, sig_y - 15, "Authorized Signature")

    def _draw_logo_placeholder(
        self,
        c: canvas.Canvas,
        x: float,
        y: float,
        size: float
    ) -> None:
        """Draw a placeholder logo."""
        c.setStrokeColor(self.colors["accent"])
        c.setLineWidth(1.5)
        center_x = x + size / 2
        center_y = y + size / 2 - 10
        radius = size / 2 - 5

        # Draw outer circle
        c.circle(center_x, center_y, radius, stroke=1, fill=0)

        # Draw inner hexagon pattern
        inner_radius = radius * 0.6
        points = []
        for i in range(6):
            angle = math.pi / 2 + i * math.pi / 3
            px = center_x + inner_radius * math.cos(angle)
            py = center_y + inner_radius * math.sin(angle)
            points.append((px, py))

        # Draw hexagon
        path = c.beginPath()
        path.moveTo(points[0][0], points[0][1])
        for px, py in points[1:]:
            path.lineTo(px, py)
        path.close()
        c.drawPath(path, stroke=1, fill=0)

    def _word_wrap(self, text: str, max_chars: int) -> List[str]:
        """
        Simple word wrapping for text.

        Args:
            text: Text to wrap
            max_chars: Maximum characters per line

        Returns:
            List of wrapped lines
        """
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line = current_line + " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines