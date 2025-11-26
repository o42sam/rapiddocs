"""
Sophisticated matplotlib-based invoice PDF generator
Generates entire invoice as a high-quality image with precise layout control
"""
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Optional, Tuple
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch
from PIL import Image as PILImage
import numpy as np

from app.schemas.invoice import InvoiceData
from app.models.document import DesignSpecification
from app.utils.logger import get_logger
from app.utils.exceptions import PDFGenerationError

logger = get_logger('invoice_pdf_matplotlib')


class MatplotlibInvoicePDFGenerator:
    """Generate professional invoice PDFs using matplotlib for precise layout control"""

    def __init__(self):
        # A5 paper size: 148mm x 210mm (5.83" x 8.27")
        self.page_width_inch = 5.83
        self.page_height_inch = 8.27
        self.dpi = 300  # High quality for PDF

        # Calculate pixel dimensions
        self.page_width_px = int(self.page_width_inch * self.dpi)
        self.page_height_px = int(self.page_height_inch * self.dpi)

        # Margins in inches
        self.margin = 0.3

    def _hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB tuple (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    def _draw_text(self, ax, x, y, text, fontsize=10, weight='normal',
                   color='black', ha='left', va='top', style='normal'):
        """Draw text at specified position"""
        ax.text(x, y, text, fontsize=fontsize, weight=weight,
                color=color, ha=ha, va=va, style=style,
                transform=ax.transData, family='sans-serif')

    def _draw_rectangle(self, ax, x, y, width, height, facecolor='none',
                        edgecolor='black', linewidth=1, alpha=1.0):
        """Draw a rectangle"""
        rect = Rectangle((x, y), width, height,
                         facecolor=facecolor, edgecolor=edgecolor,
                         linewidth=linewidth, alpha=alpha)
        ax.add_patch(rect)

    def _draw_line(self, ax, x1, y1, x2, y2, color='black', linewidth=1):
        """Draw a line"""
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth)

    def generate_invoice_pdf(
        self,
        output_path: str,
        invoice_data: InvoiceData,
        design_spec: DesignSpecification,
        logo_path: Optional[str] = None,
        use_watermark: bool = False
    ) -> str:
        """
        Generate a professional invoice PDF using matplotlib

        Args:
            output_path: Path where the PDF will be saved
            invoice_data: Complete invoice data
            design_spec: Design specifications (colors)
            logo_path: Optional company logo
            use_watermark: Whether to add logo as watermark

        Returns:
            Path to generated PDF
        """
        import tempfile

        try:
            logger.info(f"Generating matplotlib-based invoice PDF: {invoice_data.invoice_number}")

            # Get colors
            color1_rgb = self._hex_to_rgb(design_spec.foreground_color_1)
            color2_rgb = self._hex_to_rgb(design_spec.foreground_color_2)

            # Create figure with exact A5 dimensions
            fig = plt.figure(figsize=(self.page_width_inch, self.page_height_inch), dpi=self.dpi)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_xlim(0, self.page_width_inch)
            ax.set_ylim(0, self.page_height_inch)
            ax.axis('off')

            # White background
            ax.set_facecolor('white')

            # Starting Y position (from top)
            y_pos = self.page_height_inch - self.margin

            # 1. Draw Header (Logo and INVOICE title)
            y_pos = self._draw_header(ax, invoice_data, logo_path, color1_rgb, y_pos)
            y_pos -= 0.15  # Spacing

            # 2. Draw Invoice Details (Invoice #, Date, Due Date)
            y_pos = self._draw_invoice_details(ax, invoice_data, color1_rgb, y_pos)
            y_pos -= 0.15  # Spacing

            # 3. Draw Billing Information (FROM/TO)
            y_pos = self._draw_billing_info(ax, invoice_data, color1_rgb, y_pos)
            y_pos -= 0.2  # Spacing

            # 4. Draw Line Items Table
            y_pos = self._draw_line_items_table(ax, invoice_data, color1_rgb, color2_rgb, y_pos)
            y_pos -= 0.15  # Spacing

            # 5. Draw Totals Section
            y_pos = self._draw_totals(ax, invoice_data, color1_rgb, y_pos)
            y_pos -= 0.15  # Spacing

            # 6. Draw Footer (Payment Terms, Notes, Timestamp)
            self._draw_footer(ax, invoice_data, y_pos)

            # Save as temporary PNG first
            temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            plt.savefig(temp_png.name, dpi=self.dpi, bbox_inches='tight',
                       pad_inches=0, facecolor='white', edgecolor='none')
            plt.close(fig)

            # Convert PNG to PDF using ReportLab
            self._png_to_pdf(temp_png.name, output_path)

            # Clean up temp file
            os.unlink(temp_png.name)

            logger.info(f"Invoice PDF generated successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate invoice PDF: {str(e)}", exc_info=True)
            raise PDFGenerationError(
                f"Failed to generate invoice PDF: {str(e)}",
                details={'output_path': output_path, 'invoice_number': invoice_data.invoice_number}
            )

    def _draw_header(self, ax, invoice_data, logo_path, color_rgb, y_pos):
        """Draw header with logo and INVOICE title"""
        x_left = self.margin
        x_right = self.page_width_inch - self.margin

        header_height = 0.9

        # Draw logo if provided
        if logo_path and os.path.exists(logo_path):
            try:
                img = PILImage.open(logo_path)
                # Calculate logo size (max 1.2" wide, 0.8" tall)
                max_width = 1.2
                max_height = 0.8

                img_width, img_height = img.size
                aspect_ratio = img_width / img_height

                if aspect_ratio > (max_width / max_height):
                    logo_width = max_width
                    logo_height = max_width / aspect_ratio
                else:
                    logo_height = max_height
                    logo_width = max_height * aspect_ratio

                # Draw logo on left
                extent = [x_left, x_left + logo_width,
                         y_pos - logo_height, y_pos]
                ax.imshow(img, extent=extent, aspect='auto', zorder=10)
            except Exception as e:
                logger.warning(f"Failed to load logo: {str(e)}")

        # Draw INVOICE title on right
        self._draw_text(ax, x_right, y_pos, "INVOICE",
                       fontsize=20, weight='bold', color=color_rgb, ha='right', va='top')

        # Draw invoice number below title
        self._draw_text(ax, x_right, y_pos - 0.3, f"#{invoice_data.invoice_number}",
                       fontsize=10, color=color_rgb, ha='right', va='top')

        return y_pos - header_height

    def _draw_invoice_details(self, ax, invoice_data, color_rgb, y_pos):
        """Draw invoice number, date, and due date"""
        x_right = self.page_width_inch - self.margin
        line_height = 0.15

        details = [
            (f"Invoice Date:", str(invoice_data.invoice_date)),
            (f"Due Date:", str(invoice_data.due_date))
        ]

        for i, (label, value) in enumerate(details):
            y = y_pos - (i * line_height)
            # Label
            self._draw_text(ax, x_right - 1.5, y, label,
                           fontsize=8, weight='bold', color=color_rgb, ha='right', va='top')
            # Value
            self._draw_text(ax, x_right, y, value,
                           fontsize=8, ha='right', va='top')

        return y_pos - (len(details) * line_height)

    def _draw_billing_info(self, ax, invoice_data, color_rgb, y_pos):
        """Draw FROM and TO billing information"""
        x_left = self.margin
        x_mid = self.page_width_inch / 2
        line_height = 0.12

        # FROM section
        self._draw_text(ax, x_left, y_pos, "FROM:",
                       fontsize=9, weight='bold', color=color_rgb, ha='left', va='top')

        y = y_pos - 0.15
        self._draw_text(ax, x_left, y, invoice_data.bill_from_name,
                       fontsize=8, weight='bold', ha='left', va='top')

        from_lines = []
        if invoice_data.bill_from_address:
            from_lines.extend(invoice_data.bill_from_address.split('\n'))
        if invoice_data.bill_from_email:
            from_lines.append(invoice_data.bill_from_email)
        if invoice_data.bill_from_phone:
            from_lines.append(invoice_data.bill_from_phone)

        for i, line in enumerate(from_lines):
            y -= line_height
            self._draw_text(ax, x_left, y, line, fontsize=7.5, ha='left', va='top')

        # TO section
        self._draw_text(ax, x_mid, y_pos, "TO:",
                       fontsize=9, weight='bold', color=color_rgb, ha='left', va='top')

        y = y_pos - 0.15
        self._draw_text(ax, x_mid, y, invoice_data.bill_to_name,
                       fontsize=8, weight='bold', ha='left', va='top')

        to_lines = []
        if invoice_data.bill_to_address:
            to_lines.extend(invoice_data.bill_to_address.split('\n'))
        if invoice_data.bill_to_email:
            to_lines.append(invoice_data.bill_to_email)
        if invoice_data.bill_to_phone:
            to_lines.append(invoice_data.bill_to_phone)

        y_to = y_pos - 0.15
        for i, line in enumerate(to_lines):
            y_to -= line_height
            self._draw_text(ax, x_mid, y_to, line, fontsize=7.5, ha='left', va='top')

        # Return the lower of the two sections
        return min(y, y_to)

    def _draw_line_items_table(self, ax, invoice_data, color1_rgb, color2_rgb, y_pos):
        """Draw line items table with sophisticated formatting"""
        x_left = self.margin
        x_right = self.page_width_inch - self.margin
        table_width = x_right - x_left

        # Column widths (proportional)
        col_widths = [0.50, 0.12, 0.19, 0.19]  # Description, Qty, Unit Price, Amount
        col_positions = [x_left]
        for width in col_widths[:-1]:
            col_positions.append(col_positions[-1] + (table_width * width))
        col_positions.append(x_right)

        # Header row
        header_height = 0.25
        header_y_top = y_pos
        header_y_bottom = y_pos - header_height

        # Draw header background
        self._draw_rectangle(ax, x_left, header_y_bottom, table_width, header_height,
                            facecolor=color1_rgb, edgecolor=color1_rgb, linewidth=1.5)

        # Draw header text
        headers = ['Description', 'Qty', 'Unit Price', 'Amount']
        alignments = ['left', 'center', 'right', 'right']

        for i, (header, align) in enumerate(zip(headers, alignments)):
            if align == 'left':
                x = col_positions[i] + 0.05
                ha = 'left'
            elif align == 'center':
                x = (col_positions[i] + col_positions[i+1]) / 2
                ha = 'center'
            else:  # right
                x = col_positions[i+1] - 0.05
                ha = 'right'

            self._draw_text(ax, x, header_y_top - 0.08, header,
                           fontsize=8, weight='bold', color='white', ha=ha, va='top')

        # Data rows
        row_height = 0.20
        y_current = header_y_bottom

        for idx, item in enumerate(invoice_data.line_items):
            row_y_top = y_current
            row_y_bottom = y_current - row_height

            # Alternating row colors
            if idx % 2 == 0:
                row_color = (0.96, 0.96, 0.96)
            else:
                row_color = 'white'

            self._draw_rectangle(ax, x_left, row_y_bottom, table_width, row_height,
                                facecolor=row_color, edgecolor='#CCCCCC', linewidth=0.5)

            # Row data
            qty_str = f"{item.quantity:.0f}" if item.quantity == int(item.quantity) else f"{item.quantity:.2f}"
            row_data = [
                item.description,
                qty_str,
                f"${item.unit_price:,.2f}",
                f"${item.amount:,.2f}"
            ]

            for i, (data, align) in enumerate(zip(row_data, alignments)):
                if align == 'left':
                    x = col_positions[i] + 0.05
                    ha = 'left'
                elif align == 'center':
                    x = (col_positions[i] + col_positions[i+1]) / 2
                    ha = 'center'
                else:  # right
                    x = col_positions[i+1] - 0.05
                    ha = 'right'

                # Truncate long descriptions
                if i == 0 and len(data) > 50:
                    data = data[:47] + "..."

                self._draw_text(ax, x, row_y_top - 0.07, data,
                               fontsize=7.5, ha=ha, va='top', color='#333333')

            y_current = row_y_bottom

        # Draw outer border
        table_height = y_pos - y_current
        self._draw_rectangle(ax, x_left, y_current, table_width, table_height,
                            facecolor='none', edgecolor=color1_rgb, linewidth=1.5)

        return y_current

    def _draw_totals(self, ax, invoice_data, color_rgb, y_pos):
        """Draw totals section"""
        x_right = self.page_width_inch - self.margin
        line_height = 0.15

        totals_data = [
            ("Subtotal:", f"${invoice_data.subtotal:,.2f}", False)
        ]

        if invoice_data.discount_amount > 0:
            totals_data.append(("Discount:", f"-${invoice_data.discount_amount:,.2f}", False))

        if invoice_data.tax_rate > 0:
            totals_data.append((f"Tax ({invoice_data.tax_rate}%):", f"${invoice_data.tax_amount:,.2f}", False))

        totals_data.append(("TOTAL:", f"${invoice_data.total:,.2f}", True))

        y = y_pos
        for label, value, is_total in totals_data:
            if is_total:
                # Draw line above total
                self._draw_line(ax, x_right - 3.0, y + 0.05, x_right, y + 0.05,
                               color=color_rgb, linewidth=2)
                y -= 0.1

                # Total in larger, colored font
                self._draw_text(ax, x_right - 1.5, y, label,
                               fontsize=11, weight='bold', color=color_rgb, ha='right', va='top')
                self._draw_text(ax, x_right, y, value,
                               fontsize=11, weight='bold', color=color_rgb, ha='right', va='top')
            else:
                # Regular line item
                self._draw_text(ax, x_right - 1.5, y, label,
                               fontsize=9, weight='bold', ha='right', va='top')
                self._draw_text(ax, x_right, y, value,
                               fontsize=9, ha='right', va='top')

            y -= line_height

        return y

    def _draw_footer(self, ax, invoice_data, y_pos):
        """Draw payment terms, notes, and timestamp"""
        x_left = self.margin
        x_center = self.page_width_inch / 2
        line_height = 0.1

        y = y_pos

        if invoice_data.payment_terms:
            self._draw_text(ax, x_left, y, f"Payment Terms: {invoice_data.payment_terms}",
                           fontsize=7, color=(0.3, 0.3, 0.3), ha='left', va='top')
            y -= line_height

        if invoice_data.notes:
            self._draw_text(ax, x_left, y, f"Notes: {invoice_data.notes}",
                           fontsize=7, color=(0.3, 0.3, 0.3), ha='left', va='top')
            y -= line_height * 1.5

        # Timestamp at bottom center
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        self._draw_text(ax, x_center, self.margin + 0.1,
                       f"Invoice generated on {timestamp}",
                       fontsize=6, style='italic', color='gray', ha='center', va='bottom')

    def _png_to_pdf(self, png_path: str, pdf_path: str):
        """Convert PNG to PDF maintaining exact A5 dimensions"""
        from reportlab.pdfgen import canvas as rl_canvas

        c = rl_canvas.Canvas(pdf_path, pagesize=A5)

        # Draw image at exact A5 size
        c.drawImage(png_path, 0, 0,
                   width=self.page_width_inch * 72,  # Convert to points
                   height=self.page_height_inch * 72,
                   preserveAspectRatio=True)

        c.save()


# Singleton instance
matplotlib_invoice_pdf_generator = MatplotlibInvoicePDFGenerator()


# Convenience function
def generate_invoice_pdf(
    output_path: str,
    invoice_data: InvoiceData,
    design_spec: DesignSpecification,
    logo_path: Optional[str] = None,
    use_watermark: bool = False
) -> str:
    """Convenience function to generate invoice PDF using matplotlib"""
    return matplotlib_invoice_pdf_generator.generate_invoice_pdf(
        output_path,
        invoice_data,
        design_spec,
        logo_path,
        use_watermark
    )
