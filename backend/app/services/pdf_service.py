"""
PDF Generation Service for creating professional invoices
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from PIL import Image as PILImage

logger = logging.getLogger(__name__)

class PDFService:
    """Service for generating PDF documents"""

    def __init__(self):
        """Initialize PDF service"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=30
        ))

        # Company name style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            alignment=TA_LEFT,
            leading=18,
            fontName='Helvetica-Bold'
        ))

        # Address style
        self.styles.add(ParagraphStyle(
            name='Address',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_LEFT,
            leading=14
        ))

        # Invoice details style
        self.styles.add(ParagraphStyle(
            name='InvoiceDetails',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_RIGHT
        ))

    async def generate_invoice_pdf(
        self,
        invoice_data: Dict[str, Any],
        output_path: Path,
        logo_path: Optional[Path] = None
    ) -> Path:
        """Generate a professional invoice PDF"""

        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Create the PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Build the document content
            story = []

            # Add header with logo and invoice title
            story.extend(self._create_header(invoice_data, logo_path))

            # Add vendor and client information
            story.append(self._create_addresses(invoice_data))
            story.append(Spacer(1, 0.3 * inch))

            # Add line items table
            story.append(self._create_line_items_table(invoice_data))
            story.append(Spacer(1, 0.3 * inch))

            # Add totals
            story.append(self._create_totals_table(invoice_data))
            story.append(Spacer(1, 0.5 * inch))

            # Add payment terms and notes
            story.extend(self._create_footer(invoice_data))

            # Build the PDF
            doc.build(story)

            logger.info(f"Invoice PDF generated successfully at {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise

    def _create_header(self, invoice_data: Dict, logo_path: Optional[Path]) -> list:
        """Create the header section with logo and title"""
        elements = []

        # Create a table for the header layout
        header_data = []
        header_row = []

        # Logo or company name
        if logo_path and logo_path.exists():
            try:
                img = Image(str(logo_path), width=2*inch, height=1*inch)
                img.hAlign = 'LEFT'
                header_row.append(img)
            except Exception as e:
                logger.warning(f"Failed to load logo: {e}")
                header_row.append(Paragraph(invoice_data.get('vendor_name', 'Company'), self.styles['CompanyName']))
        else:
            header_row.append(Paragraph(invoice_data.get('vendor_name', 'Company'), self.styles['CompanyName']))

        # Invoice title and number
        invoice_info = f"""
        <para align="right">
        <b>INVOICE</b><br/>
        <font size="10">#{invoice_data.get('invoice_number', 'INV-001')}</font><br/>
        <font size="9">{datetime.now().strftime('%B %d, %Y')}</font>
        </para>
        """
        header_row.append(Paragraph(invoice_info, self.styles['InvoiceDetails']))

        header_data.append(header_row)

        header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _create_addresses(self, invoice_data: Dict) -> Table:
        """Create the vendor and client address section"""

        vendor_address = invoice_data.get('vendor_address', 'Vendor Address').replace('\n', '<br/>')
        vendor_info = f"""
        <para>
        <b>From:</b><br/>
        {invoice_data.get('vendor_name', 'Vendor Name')}<br/>
        {vendor_address}
        </para>
        """

        client_address = invoice_data.get('client_address', 'Client Address').replace('\n', '<br/>')
        client_info = f"""
        <para>
        <b>Bill To:</b><br/>
        {invoice_data.get('client_name', 'Client Name')}<br/>
        {client_address}
        </para>
        """

        address_data = [[
            Paragraph(vendor_info, self.styles['Address']),
            Paragraph(client_info, self.styles['Address'])
        ]]

        address_table = Table(address_data, colWidths=[3.25*inch, 3.25*inch])
        address_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        return address_table

    def _create_line_items_table(self, invoice_data: Dict) -> Table:
        """Create the line items table"""

        # Headers
        headers = ['Description', 'Qty', 'Unit Price', 'Tax', 'Total']

        # Table data
        data = [headers]

        currency = invoice_data.get('currency', 'USD')
        currency_symbol = {'USD': '$', 'EUR': '€', 'GBP': '£'}.get(currency, '$')

        # Add line items
        for item in invoice_data.get('line_items', []):
            qty = float(item.get('quantity', 0))
            unit_price = float(item.get('unit_price', 0))
            tax_rate = float(item.get('tax_rate', 0))

            subtotal = qty * unit_price
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount

            data.append([
                item.get('description', ''),
                str(int(qty)),
                f"{currency_symbol}{unit_price:,.2f}",
                f"{tax_rate*100:.0f}%",
                f"{currency_symbol}{total:,.2f}"
            ])

        # Create table
        table = Table(data, colWidths=[3*inch, 0.75*inch, 1.25*inch, 0.75*inch, 1.25*inch])

        # Style the table
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),

            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        return table

    def _create_totals_table(self, invoice_data: Dict) -> Table:
        """Create the totals section"""

        currency = invoice_data.get('currency', 'USD')
        currency_symbol = {'USD': '$', 'EUR': '€', 'GBP': '£'}.get(currency, '$')

        # Calculate totals
        subtotal = 0
        total_tax = 0

        for item in invoice_data.get('line_items', []):
            qty = float(item.get('quantity', 0))
            unit_price = float(item.get('unit_price', 0))
            tax_rate = float(item.get('tax_rate', 0))

            item_subtotal = qty * unit_price
            subtotal += item_subtotal
            total_tax += item_subtotal * tax_rate

        grand_total = subtotal + total_tax

        # Create totals data
        totals_data = [
            ['', 'Subtotal:', f"{currency_symbol}{subtotal:,.2f}"],
            ['', 'Tax:', f"{currency_symbol}{total_tax:,.2f}"],
            ['', 'Total:', f"{currency_symbol}{grand_total:,.2f}"]
        ]

        # Create table
        totals_table = Table(totals_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])

        # Style the table
        totals_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (1, -1), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, -1), (2, -1), 12),
            ('BACKGROUND', (1, -1), (2, -1), colors.HexColor('#e8f4f8')),
            ('GRID', (1, -1), (2, -1), 1, colors.HexColor('#2c3e50')),
            ('LEFTPADDING', (1, 0), (-1, -1), 12),
            ('RIGHTPADDING', (1, 0), (-1, -1), 12),
            ('TOPPADDING', (1, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (1, 0), (-1, -1), 8),
        ]))

        return totals_table

    def _create_footer(self, invoice_data: Dict) -> list:
        """Create footer with payment terms and notes"""
        elements = []

        # Payment terms
        payment_terms = invoice_data.get('payment_terms', 'Net 30 days')
        terms_para = Paragraph(f"<b>Payment Terms:</b> {payment_terms}", self.styles['Normal'])
        elements.append(terms_para)
        elements.append(Spacer(1, 0.2 * inch))

        # Notes
        notes = invoice_data.get('notes', 'Thank you for your business!')
        notes_para = Paragraph(f"<b>Notes:</b> {notes}", self.styles['Normal'])
        elements.append(notes_para)

        return elements