"""
Invoice PDF layout generator - creates professional invoice PDFs in A5 size
"""
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors as rl_colors
from datetime import datetime
from typing import Optional, Tuple
import os
import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.table import Table as MplTable

from app.schemas.invoice import InvoiceData
from app.models.document import DesignSpecification
from app.utils.logger import get_logger
from app.utils.exceptions import PDFGenerationError

logger = get_logger('invoice_pdf')


class InvoicePDFGenerator:
    """Generate professional invoice PDFs in A5 size (148mm x 210mm)"""

    def __init__(self):
        # A5 paper size: 148mm x 210mm (5.83" x 8.27")
        self.page_width, self.page_height = A5
        self.margin = 0.3 * inch  # Even smaller margins for A5 to fit on one page

    def _hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB tuple (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    def _generate_matplotlib_table(
        self,
        invoice_data: InvoiceData,
        color1,
        color2,
        temp_path: str
    ) -> str:
        """
        Generate a sophisticated table using matplotlib for line items

        Args:
            invoice_data: Invoice data with line items
            color1: Primary color (header background)
            color2: Secondary color (accents)
            temp_path: Path to save the table image

        Returns:
            Path to the generated table image
        """
        logger.info("Generating matplotlib-based line items table")

        # Get RGB values for matplotlib
        header_color = self._hex_to_rgb(f"#{int(color1.red*255):02x}{int(color1.green*255):02x}{int(color1.blue*255):02x}")
        accent_color = self._hex_to_rgb(f"#{int(color2.red*255):02x}{int(color2.green*255):02x}{int(color2.blue*255):02x}")

        # Prepare data
        headers = ['Description', 'Qty', 'Unit Price', 'Amount']
        rows = []
        for item in invoice_data.line_items:
            rows.append([
                item.description,
                f"{item.quantity:.0f}" if item.quantity == int(item.quantity) else f"{item.quantity:.2f}",
                f"${item.unit_price:,.2f}",
                f"${item.amount:,.2f}"
            ])

        # Calculate figure size for A5 width (5.2 inches usable width with smaller margins)
        fig_width = 5.2
        row_height = 0.28  # Reduced row height
        header_height = 0.38  # Reduced header height
        fig_height = header_height + (len(rows) * row_height)

        # Create figure
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=150)
        ax.axis('off')

        # Create table
        table_data = [headers] + rows
        table = ax.table(
            cellText=table_data,
            cellLoc='left',
            loc='center',
            bbox=[0, 0, 1, 1]
        )

        # Style the table
        table.auto_set_font_size(False)

        # Column widths (normalized to 1.0)
        col_widths = [0.48, 0.12, 0.20, 0.20]  # Description, Qty, Unit Price, Amount

        for i, width in enumerate(col_widths):
            for j in range(len(table_data)):
                cell = table[(j, i)]
                cell.set_width(width)

        # Style header row
        for i in range(len(headers)):
            cell = table[(0, i)]
            cell.set_facecolor(header_color)
            cell.set_text_props(
                weight='bold',
                color='white',
                fontsize=8,  # Reduced from 10
                ha='left' if i == 0 else 'center' if i == 1 else 'right'
            )
            cell.set_height(header_height / fig_height)
            cell.set_edgecolor('white')
            cell.set_linewidth(1)

        # Style data rows
        for row_idx in range(1, len(table_data)):
            for col_idx in range(len(headers)):
                cell = table[(row_idx, col_idx)]

                # Alternating row colors
                if row_idx % 2 == 0:
                    cell.set_facecolor('#F5F5F5')
                else:
                    cell.set_facecolor('white')

                # Text alignment
                if col_idx == 0:  # Description - left align
                    alignment = 'left'
                elif col_idx == 1:  # Qty - center align
                    alignment = 'center'
                else:  # Price columns - right align
                    alignment = 'right'

                cell.set_text_props(
                    fontsize=7.5,  # Reduced from 9
                    ha=alignment,
                    color='#333333'
                )
                cell.set_height(row_height / fig_height)
                cell.set_edgecolor('#CCCCCC')
                cell.set_linewidth(0.5)

        # Add subtle border around entire table
        for key, cell in table.get_celld().items():
            if key[0] == 0:  # Header row
                cell.set_edgecolor(header_color)
                cell.set_linewidth(1.5)
            elif key[0] == len(table_data) - 1:  # Last row
                cell.set_linewidth(1)

        # Save figure
        plt.tight_layout(pad=0.1)
        plt.savefig(
            temp_path,
            dpi=150,
            bbox_inches='tight',
            pad_inches=0.05,
            facecolor='white',
            edgecolor='none'
        )
        plt.close(fig)

        logger.info(f"Matplotlib table saved to: {temp_path}")
        return temp_path

    def _create_color(self, hex_color: str):
        """Create ReportLab color from hex"""
        r, g, b = self._hex_to_rgb(hex_color)
        return rl_colors.Color(r, g, b)

    def generate_invoice_pdf(
        self,
        output_path: str,
        invoice_data: InvoiceData,
        design_spec: DesignSpecification,
        logo_path: Optional[str] = None,
        use_watermark: bool = False
    ) -> str:
        """
        Generate a professional invoice PDF

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
        import shutil

        temp_dir = None
        try:
            logger.info(f"Generating invoice PDF: {invoice_data.invoice_number}")

            # Create temporary directory for matplotlib table images
            temp_dir = tempfile.mkdtemp(prefix="invoice_tables_")
            logger.debug(f"Created temp directory: {temp_dir}")

            # Create PDF document with A5 size
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A5,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )

            # Get colors
            color1 = self._create_color(design_spec.foreground_color_1)
            color2 = self._create_color(design_spec.foreground_color_2)

            # Build elements
            elements = []

            # Header section
            elements.extend(self._create_header(invoice_data, logo_path, color1))

            # Invoice details section
            elements.extend(self._create_invoice_details(invoice_data, color1, color2))

            # Billing information section
            elements.extend(self._create_billing_info(invoice_data, color1))

            # Line items table (with matplotlib)
            elements.extend(self._create_line_items_table(invoice_data, color1, color2, temp_dir))

            # Totals section
            elements.extend(self._create_totals_section(invoice_data, color1))

            # Payment terms and notes
            elements.extend(self._create_footer(invoice_data))

            # Build PDF
            doc.build(elements)

            logger.info(f"Invoice PDF generated successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate invoice PDF: {str(e)}", exc_info=True)
            raise PDFGenerationError(
                f"Failed to generate invoice PDF: {str(e)}",
                details={'output_path': output_path, 'invoice_number': invoice_data.invoice_number}
            )
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp directory: {str(e)}")

    def _create_header(self, invoice_data: InvoiceData, logo_path: Optional[str], color1) -> list:
        """Create invoice header with logo and title"""
        elements = []
        styles = getSampleStyleSheet()

        # Header table: Logo on left, INVOICE title on right
        header_data = []

        if logo_path and os.path.exists(logo_path):
            try:
                # Logo sizing for A5 - smaller for single page fit
                # Using kind='bound' to ensure logo fits within bounds while maintaining aspect ratio
                from PIL import Image as PILImage

                # Get image dimensions
                pil_img = PILImage.open(logo_path)
                img_width, img_height = pil_img.size
                aspect_ratio = img_width / img_height

                # Calculate optimal size (max 1.2" wide, 0.9" tall for A5)
                max_width = 1.2 * inch
                max_height = 0.9 * inch

                if aspect_ratio > (max_width / max_height):
                    # Width-constrained
                    logo_width = max_width
                    logo_height = max_width / aspect_ratio
                else:
                    # Height-constrained
                    logo_height = max_height
                    logo_width = max_height * aspect_ratio

                logo = Image(logo_path, width=logo_width, height=logo_height)
                # Invoice title with invoice number - smaller for single page
                invoice_header_text = f"<font size='18'><b>INVOICE</b></font><br/><font size='10'>#{invoice_data.invoice_number}</font>"
                invoice_title = Paragraph(
                    invoice_header_text,
                    ParagraphStyle(
                        'InvoiceTitle',
                        parent=styles['Title'],
                        fontSize=18,
                        textColor=color1,
                        alignment=TA_RIGHT,
                        leading=22
                    )
                )
                header_data = [[logo, invoice_title]]
            except Exception as e:
                logger.warning(f"Failed to load logo: {str(e)}")
                # If logo fails, use title with invoice number
                invoice_header_text = f"<font size='18'><b>INVOICE</b></font><br/><font size='10'>#{invoice_data.invoice_number}</font>"
                invoice_title = Paragraph(
                    invoice_header_text,
                    ParagraphStyle(
                        'InvoiceTitle',
                        parent=styles['Title'],
                        fontSize=18,
                        textColor=color1,
                        alignment=TA_CENTER,
                        leading=22
                    )
                )
                header_data = [[invoice_title]]
        else:
            # No logo - show title with invoice number centered
            invoice_header_text = f"<font size='18'><b>INVOICE</b></font><br/><font size='10'>#{invoice_data.invoice_number}</font>"
            invoice_title = Paragraph(
                invoice_header_text,
                ParagraphStyle(
                    'InvoiceTitle',
                    parent=styles['Title'],
                    fontSize=18,
                    textColor=color1,
                    alignment=TA_CENTER,
                    leading=22
                )
            )
            header_data = [[invoice_title]]

        if header_data[0]:
            # Adjust column widths for A5 (total width ~5.2 inches with smaller margins)
            header_table = Table(header_data, colWidths=[1.2*inch, 4.0*inch] if len(header_data[0]) == 2 else [5.2*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT') if len(header_data[0]) == 2 else ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(header_table)

        elements.append(Spacer(1, 0.1*inch))  # Reduced spacing for single-page fit

        return elements

    def _create_invoice_details(self, invoice_data: InvoiceData, color1, color2) -> list:
        """Create invoice number and dates section"""
        elements = []
        styles = getSampleStyleSheet()

        # Invoice details in a table
        details_style = ParagraphStyle(
            'InvoiceDetails',
            parent=styles['Normal'],
            fontSize=8,  # Reduced from 10
            alignment=TA_RIGHT
        )

        label_style = ParagraphStyle(
            'InvoiceLabels',
            parent=styles['Normal'],
            fontSize=8,  # Reduced from 10
            textColor=color1,
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT
        )

        details_data = [
            [
                Paragraph("<b>Invoice Number:</b>", label_style),
                Paragraph(str(invoice_data.invoice_number), details_style)
            ],
            [
                Paragraph("<b>Invoice Date:</b>", label_style),
                Paragraph(str(invoice_data.invoice_date), details_style)
            ],
            [
                Paragraph("<b>Due Date:</b>", label_style),
                Paragraph(str(invoice_data.due_date), details_style)
            ]
        ]

        # Adjust for A5
        details_table = Table(details_data, colWidths=[1.5*inch, 1.5*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('RIGHTPADDING', (0, 0), (0, -1), 10),
        ]))

        # Align table to the right
        details_table.hAlign = 'RIGHT'
        elements.append(details_table)
        elements.append(Spacer(1, 0.1*inch))  # Reduced spacing for single-page fit

        return elements

    def _create_billing_info(self, invoice_data: InvoiceData, color1) -> list:
        """Create bill from/bill to section"""
        elements = []
        styles = getSampleStyleSheet()

        heading_style = ParagraphStyle(
            'BillingHeading',
            parent=styles['Normal'],
            fontSize=9,  # Reduced from 12
            textColor=color1,
            fontName='Helvetica-Bold',
            spaceAfter=4
        )

        info_style = ParagraphStyle(
            'BillingInfo',
            parent=styles['Normal'],
            fontSize=8,  # Reduced from 10
            leading=11  # Reduced from 14
        )

        # Build bill from text
        bill_from_text = f"<b>{invoice_data.bill_from_name}</b><br/>"
        if invoice_data.bill_from_address:
            bill_from_text += invoice_data.bill_from_address.replace('\n', '<br/>') + "<br/>"
        if invoice_data.bill_from_email:
            bill_from_text += invoice_data.bill_from_email + "<br/>"
        if invoice_data.bill_from_phone:
            bill_from_text += invoice_data.bill_from_phone

        # Build bill to text
        bill_to_text = f"<b>{invoice_data.bill_to_name}</b><br/>"
        if invoice_data.bill_to_address:
            bill_to_text += invoice_data.bill_to_address.replace('\n', '<br/>') + "<br/>"
        if invoice_data.bill_to_email:
            bill_to_text += invoice_data.bill_to_email + "<br/>"
        if invoice_data.bill_to_phone:
            bill_to_text += invoice_data.bill_to_phone

        billing_data = [
            [
                Paragraph("FROM:", heading_style),
                Paragraph("TO:", heading_style)
            ],
            [
                Paragraph(bill_from_text, info_style),
                Paragraph(bill_to_text, info_style)
            ]
        ]

        # Adjust for A5 with smaller margins
        billing_table = Table(billing_data, colWidths=[2.6*inch, 2.6*inch])
        billing_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))

        elements.append(billing_table)
        elements.append(Spacer(1, 0.12*inch))  # Reduced spacing for single-page fit

        return elements

    def _create_line_items_table(self, invoice_data: InvoiceData, color1, color2, temp_dir: str) -> list:
        """Create line items table using matplotlib for sophisticated formatting"""
        elements = []

        # Generate matplotlib table as image
        import tempfile
        table_image_path = os.path.join(temp_dir, f"table_{invoice_data.invoice_number}.png")

        try:
            self._generate_matplotlib_table(invoice_data, color1, color2, table_image_path)

            # Load the generated image into ReportLab
            table_image = Image(table_image_path, width=5.2*inch, height=None)
            elements.append(table_image)
            elements.append(Spacer(1, 0.1*inch))  # Spacing after table

        except Exception as e:
            logger.error(f"Failed to generate matplotlib table, falling back to ReportLab: {str(e)}")
            # Fallback to original ReportLab table if matplotlib fails
            elements.extend(self._create_line_items_table_fallback(invoice_data, color1, color2))

        return elements

    def _create_line_items_table_fallback(self, invoice_data: InvoiceData, color1, color2) -> list:
        """Fallback: Create line items table using ReportLab"""
        elements = []
        styles = getSampleStyleSheet()

        # Table header
        header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=8,  # Reduced to match matplotlib table
            textColor=rl_colors.white,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        )

        # Header row
        table_data = [[
            Paragraph("Description", header_style),
            Paragraph("Qty", header_style),
            Paragraph("Unit Price", header_style),
            Paragraph("Amount", header_style)
        ]]

        # Line items
        item_style = ParagraphStyle(
            'LineItem',
            parent=styles['Normal'],
            fontSize=7.5,  # Reduced to match matplotlib table
            leading=9
        )

        for item in invoice_data.line_items:
            table_data.append([
                Paragraph(item.description, item_style),
                Paragraph(str(item.quantity), item_style),
                Paragraph(f"${item.unit_price:,.2f}", item_style),
                Paragraph(f"${item.amount:,.2f}", item_style)
            ])

        # Create table - adjusted for A5 width (~5.2" usable with smaller margins)
        line_items_table = Table(
            table_data,
            colWidths=[2.5*inch, 0.7*inch, 1.0*inch, 1.0*inch]
        )

        # Style the table
        header_bg = color1
        line_items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), header_bg),
            ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (-1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, rl_colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, header_bg),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [rl_colors.white, rl_colors.Color(0.95, 0.95, 0.95)])
        ]))

        elements.append(line_items_table)
        elements.append(Spacer(1, 0.15*inch))

        return elements

    def _create_totals_section(self, invoice_data: InvoiceData, color1) -> list:
        """Create totals section"""
        elements = []
        styles = getSampleStyleSheet()

        label_style = ParagraphStyle(
            'TotalLabel',
            parent=styles['Normal'],
            fontSize=9,  # Reduced from 11
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        )

        value_style = ParagraphStyle(
            'TotalValue',
            parent=styles['Normal'],
            fontSize=9,  # Reduced from 11
            alignment=TA_RIGHT
        )

        total_label_style = ParagraphStyle(
            'FinalTotalLabel',
            parent=styles['Normal'],
            fontSize=11,  # Reduced from 14
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            textColor=color1
        )

        total_value_style = ParagraphStyle(
            'FinalTotalValue',
            parent=styles['Normal'],
            fontSize=11,  # Reduced from 14
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            textColor=color1
        )

        totals_data = [
            [Paragraph("Subtotal:", label_style), Paragraph(f"${invoice_data.subtotal:,.2f}", value_style)],
        ]

        if invoice_data.discount_amount > 0:
            totals_data.append([
                Paragraph("Discount:", label_style),
                Paragraph(f"-${invoice_data.discount_amount:,.2f}", value_style)
            ])

        if invoice_data.tax_rate > 0:
            totals_data.append([
                Paragraph(f"Tax ({invoice_data.tax_rate}%):", label_style),
                Paragraph(f"${invoice_data.tax_amount:,.2f}", value_style)
            ])

        totals_data.append([
            Paragraph("TOTAL:", total_label_style),
            Paragraph(f"${invoice_data.total:,.2f}", total_value_style)
        ])

        totals_table = Table(totals_data, colWidths=[1.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -2), 4),  # Reduced from 6
            ('BOTTOMPADDING', (0, 0), (-1, -2), 4),  # Reduced from 6
            ('TOPPADDING', (0, -1), (-1, -1), 6),  # Reduced from 10
            ('BOTTOMPADDING', (0, -1), (-1, -1), 6),  # Reduced from 10
            ('LINEABOVE', (0, -1), (-1, -1), 2, color1),
        ]))

        totals_table.hAlign = 'RIGHT'
        elements.append(totals_table)
        elements.append(Spacer(1, 0.1*inch))  # Reduced spacing for single-page fit

        return elements

    def _create_footer(self, invoice_data: InvoiceData) -> list:
        """Create payment terms and notes footer"""
        elements = []
        styles = getSampleStyleSheet()

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=7,  # Reduced from 8 for single-page fit
            leading=9,  # Reduced from 10 for tighter spacing
            textColor=rl_colors.Color(0.3, 0.3, 0.3)
        )

        if invoice_data.payment_terms:
            elements.append(Paragraph(f"<b>Payment Terms:</b> {invoice_data.payment_terms}", footer_style))
            elements.append(Spacer(1, 0.04*inch))  # Reduced from 0.05

        if invoice_data.notes:
            elements.append(Paragraph(f"<b>Notes:</b> {invoice_data.notes}", footer_style))
            elements.append(Spacer(1, 0.06*inch))  # Reduced from 0.1

        # Generated timestamp
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        elements.append(Paragraph(
            f"<i>Invoice generated on {timestamp}</i>",
            ParagraphStyle(
                'Timestamp',
                parent=styles['Normal'],
                fontSize=6,  # Reduced from 7
                textColor=rl_colors.grey,
                alignment=TA_CENTER
            )
        ))

        return elements


# Singleton instance
invoice_pdf_generator = InvoicePDFGenerator()


# For testing - will be used in pdf_generator.py
def generate_invoice_pdf(
    output_path: str,
    invoice_data: InvoiceData,
    design_spec: DesignSpecification,
    logo_path: Optional[str] = None,
    use_watermark: bool = False
) -> str:
    """Convenience function to generate invoice PDF"""
    return invoice_pdf_generator.generate_invoice_pdf(
        output_path,
        invoice_data,
        design_spec,
        logo_path,
        use_watermark
    )
