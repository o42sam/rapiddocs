"""
Simple invoice PDF generator using FPDF
Based on user-provided code for clean, borderless invoice layout
"""
from fpdf import FPDF
import os
from typing import List, Dict, Optional
from app.utils.logger import get_logger

logger = get_logger('invoice_pdf_fpdf')


class InvoicePDFGenerator:
    """Generate simple invoice PDFs using FPDF"""

    def generate_invoice(
        self,
        items: List[Dict],
        output_path: str,
        logo_path: Optional[str] = None,
        header_text: str = "INVOICE"
    ) -> str:
        """
        Generate a PDF invoice with a centered logo, header, and borderless item table.

        Args:
            items: List of dictionaries with keys 'item', 'quantity', 'price'
            output_path: Path to save the generated PDF
            logo_path: Optional path to logo image file
            header_text: Header text to display below logo

        Returns:
            Path to generated PDF file
        """
        logger.info(f"Generating invoice PDF: {output_path}")
        logger.debug(f"Items count: {len(items)}, Logo: {logo_path}, Header: {header_text}")

        # Initialize PDF document
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_margins(0, 0, 0)  # Disable automatic margins
        pdf.set_auto_page_break(auto=False)  # Disable auto page break
        pdf.add_page()

        # Page dimensions
        page_width = 210  # A4 width in mm
        page_height = 297  # A4 height in mm

        # 1. Add Logo (centered at top)
        logo_y = 15
        if logo_path and os.path.exists(logo_path):
            logger.debug(f"Adding logo: {logo_path}")
            # Calculate centered position
            logo_width = 50  # Fixed width for logo
            logo_x = (page_width - logo_width) / 2

            # Add logo
            try:
                pdf.image(logo_path, x=logo_x, y=logo_y, w=logo_width)
                # FPDF doesn't provide easy access to rendered height, estimate based on aspect ratio
                # Assume square logo for simplicity
                logo_height = 50  # Approximate height
                current_y = logo_y + logo_height + 5  # Position below logo
            except Exception as e:
                logger.warning(f"Failed to add logo: {e}")
                current_y = 25  # Fallback position
        else:
            current_y = 25  # Default starting position without logo
            logger.debug("No logo provided, starting at default position")

        # 2. Add Header Text
        pdf.set_font("Arial", 'B', 18)
        pdf.set_y(current_y)
        pdf.cell(0, 10, header_text, align='C', ln=True)
        current_y = pdf.get_y() + 10  # Move below header

        # 3. Create Table
        col_widths = [90, 40, 40]  # Column widths for Item, Qty, Price
        table_width = sum(col_widths)
        table_x = (page_width - table_width) / 2  # Center table horizontally

        # Table Header
        pdf.set_font("Arial", 'B', 12)
        pdf.set_y(current_y)
        headers = ["Item Description", "Quantity", "Price"]
        for i, header in enumerate(headers):
            pdf.set_x(table_x + sum(col_widths[:i]))
            align = 'L' if i == 0 else 'R'  # Left align first column, right align others
            pdf.cell(col_widths[i], 10, header, border=0, align=align)
        current_y = pdf.get_y() + 10

        # Table Rows
        pdf.set_font("Arial", size=11)
        for item in items:
            pdf.set_y(current_y)

            # Item description (left aligned)
            pdf.set_x(table_x)
            pdf.cell(col_widths[0], 10, str(item['item']), border=0, align='L')

            # Quantity (center aligned)
            pdf.set_x(table_x + col_widths[0])
            pdf.cell(col_widths[1], 10, str(item['quantity']), border=0, align='C')

            # Price (right aligned)
            pdf.set_x(table_x + col_widths[0] + col_widths[1])
            pdf.cell(col_widths[2], 10, f"${item['price']:.2f}", border=0, align='R')

            current_y += 10  # Move to next row position

        # 4. Add Total
        total = sum(item['quantity'] * item['price'] for item in items)
        pdf.set_y(current_y + 5)  # Space before total
        pdf.set_font("Arial", 'B', 12)

        # "Total" label (spans first two columns)
        pdf.set_x(table_x)
        pdf.cell(col_widths[0] + col_widths[1], 10, "TOTAL:", border=0, align='R')

        # Total value
        pdf.set_x(table_x + col_widths[0] + col_widths[1])
        pdf.cell(col_widths[2], 10, f"${total:.2f}", border=0, align='R')

        # Save PDF
        pdf.output(output_path)
        logger.info(f"Invoice PDF generated successfully: {output_path}")
        logger.info(f"Total amount: ${total:.2f}")

        return output_path


# Singleton instance
fpdf_invoice_generator = InvoicePDFGenerator()
