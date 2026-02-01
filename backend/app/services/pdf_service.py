"""
PDF Generation Service for creating professional invoices
"""
import os
import logging
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.utils import ImageReader
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
        """Generate a professional invoice PDF to file (legacy method)"""

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

    async def generate_invoice_pdf_bytes(
        self,
        invoice_data: Dict[str, Any],
        logo_bytes: Optional[bytes] = None
    ) -> bytes:
        """
        Generate a professional invoice PDF and return as bytes.
        This method stores everything in memory, no filesystem access needed.

        Args:
            invoice_data: Invoice data dictionary
            logo_bytes: Optional logo image as bytes

        Returns:
            PDF document as bytes
        """
        try:
            # Create a BytesIO buffer for the PDF
            buffer = BytesIO()

            # Create the PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Build the document content
            story = []

            # Add header with logo and invoice title
            story.extend(self._create_header_from_bytes(invoice_data, logo_bytes))

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

            # Get the PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(f"Invoice PDF generated successfully ({len(pdf_bytes)} bytes)")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise

    def _create_header_from_bytes(self, invoice_data: Dict, logo_bytes: Optional[bytes]) -> list:
        """Create the header section with logo from bytes and title"""
        elements = []

        # Create a table for the header layout
        header_data = []
        header_row = []

        # Logo or company name
        if logo_bytes:
            try:
                # Create an ImageReader from bytes
                logo_buffer = BytesIO(logo_bytes)
                img = Image(logo_buffer, width=2*inch, height=1*inch)
                img.hAlign = 'LEFT'
                header_row.append(img)
            except Exception as e:
                logger.warning(f"Failed to load logo from bytes: {e}")
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

    # ========== FORMAL DOCUMENT GENERATION ==========

    def _setup_formal_styles(self):
        """Setup custom styles for formal documents"""
        # Document title style
        if 'FormalTitle' not in [s.name for s in self.styles.byName.values()]:
            self.styles.add(ParagraphStyle(
                name='FormalTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a2e'),
                alignment=TA_CENTER,
                spaceAfter=20,
                spaceBefore=10,
                fontName='Helvetica-Bold'
            ))

        # Section heading style
        if 'FormalHeading' not in [s.name for s in self.styles.byName.values()]:
            self.styles.add(ParagraphStyle(
                name='FormalHeading',
                parent=self.styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2c3e50'),
                spaceBefore=16,
                spaceAfter=8,
                fontName='Helvetica-Bold'
            ))

        # Body text style
        if 'FormalBody' not in [s.name for s in self.styles.byName.values()]:
            self.styles.add(ParagraphStyle(
                name='FormalBody',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#333333'),
                alignment=TA_LEFT,
                spaceBefore=6,
                spaceAfter=6,
                leading=16,
                firstLineIndent=0
            ))

        # Indented paragraph style (for sub-points)
        if 'FormalIndented' not in [s.name for s in self.styles.byName.values()]:
            self.styles.add(ParagraphStyle(
                name='FormalIndented',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#333333'),
                leftIndent=24,
                spaceBefore=4,
                spaceAfter=4,
                leading=15
            ))

        # Double indented style
        if 'FormalDoubleIndent' not in [s.name for s in self.styles.byName.values()]:
            self.styles.add(ParagraphStyle(
                name='FormalDoubleIndent',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#333333'),
                leftIndent=48,
                spaceBefore=3,
                spaceAfter=3,
                leading=14
            ))

        # Footer/date style
        if 'FormalFooter' not in [s.name for s in self.styles.byName.values()]:
            self.styles.add(ParagraphStyle(
                name='FormalFooter',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER
            ))

    async def generate_formal_document_pdf_bytes(
        self,
        document_data: Dict[str, Any],
        content: str,
        logo_bytes: Optional[bytes] = None,
        color_scheme: Optional[List[str]] = None,
        use_watermark: bool = False,
        edge_decorations: bool = True
    ) -> bytes:
        """
        Generate a formal document PDF and return as bytes.

        Args:
            document_data: Document metadata (title, author, date, etc.)
            content: The generated text content
            logo_bytes: Optional logo image as bytes
            color_scheme: List of hex color codes for decoration
            use_watermark: Whether to add watermark (requires logo_bytes)
            edge_decorations: Whether to add decorative lines on edges

        Returns:
            PDF document as bytes
        """
        try:
            # Setup formal document styles
            self._setup_formal_styles()

            # Create a BytesIO buffer for the PDF
            buffer = BytesIO()

            # Create the PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Build the document content
            story = []

            # Default color scheme
            if not color_scheme or len(color_scheme) < 3:
                color_scheme = ['#1a1a2e', '#16213e', '#0f3460']

            # Add cover page / header
            story.extend(self._create_formal_header(document_data, logo_bytes, color_scheme))

            # Add main content
            story.extend(self._format_formal_content(content, color_scheme))

            # Add footer with date and page info
            story.extend(self._create_formal_footer(document_data))

            # Build with edge decorations if enabled
            if edge_decorations:
                doc.build(
                    story,
                    onFirstPage=lambda c, d: self._add_edge_decorations(c, d, color_scheme),
                    onLaterPages=lambda c, d: self._add_edge_decorations(c, d, color_scheme)
                )
            else:
                doc.build(story)

            # Get the PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(f"Formal document PDF generated successfully ({len(pdf_bytes)} bytes)")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Failed to generate formal document PDF: {e}")
            raise

    def _create_formal_header(
        self,
        document_data: Dict,
        logo_bytes: Optional[bytes],
        color_scheme: List[str]
    ) -> list:
        """Create the header section for formal document"""
        elements = []

        # Add logo if provided
        if logo_bytes:
            try:
                logo_buffer = BytesIO(logo_bytes)
                img = Image(logo_buffer, width=1.5*inch, height=0.75*inch)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(1, 0.3 * inch))
            except Exception as e:
                logger.warning(f"Failed to add logo to formal document: {e}")

        # Document title
        title = document_data.get('title', 'Formal Document')
        # Escape HTML special characters
        title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        title_para = Paragraph(title, self.styles['FormalTitle'])
        elements.append(title_para)
        elements.append(Spacer(1, 0.2 * inch))

        # Author and date line
        author = document_data.get('author', '')
        date = document_data.get('date', '')

        if author or date:
            meta_text = []
            if author:
                meta_text.append(f"Author: {author}")
            if date:
                meta_text.append(f"Date: {date}")
            meta_para = Paragraph(" | ".join(meta_text), self.styles['FormalFooter'])
            elements.append(meta_para)

        elements.append(Spacer(1, 0.4 * inch))

        # Add a horizontal line
        from reportlab.platypus import HRFlowable
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor(color_scheme[0]),
            spaceAfter=20
        ))

        return elements

    def _format_formal_content(self, content: str, color_scheme: List[str]) -> list:
        """Format the main content into proper PDF elements"""
        elements = []

        # Split content into paragraphs
        paragraphs = content.split('\n')

        for para in paragraphs:
            para = para.strip()
            if not para:
                elements.append(Spacer(1, 0.1 * inch))
                continue

            # Escape HTML special characters
            para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            # Detect heading patterns (lines that look like section titles)
            # Usually short, possibly numbered, and followed by content
            is_heading = False

            # Check for numbered main headings like "1. Introduction" or "2. Background"
            import re
            heading_match = re.match(r'^(\d+)\.\s+([A-Z][^\.]{3,50})$', para)
            if heading_match:
                is_heading = True
                para = f"<b>{para}</b>"

            # Check for title-like lines (short, capitalized, no period)
            elif len(para) < 60 and not para.endswith('.') and para[0].isupper():
                # Could be a title/heading
                words = para.split()
                if len(words) <= 6:
                    is_heading = True
                    para = f"<b>{para}</b>"

            # Determine indentation level
            original_para = para
            indent_level = 0

            # Check for lettered sub-points (a., b., c.)
            if re.match(r'^[a-z]\.\s', para):
                indent_level = 1
            # Check for roman numeral sub-sub-points (i., ii., iii.)
            elif re.match(r'^(i{1,3}|iv|vi{0,3}|ix|x)\.\s', para, re.IGNORECASE):
                indent_level = 2

            # Select appropriate style
            if is_heading:
                style = self.styles['FormalHeading']
            elif indent_level == 2:
                style = self.styles['FormalDoubleIndent']
            elif indent_level == 1:
                style = self.styles['FormalIndented']
            else:
                style = self.styles['FormalBody']

            try:
                p = Paragraph(para, style)
                elements.append(p)
            except Exception as e:
                # If paragraph fails, try with plain text
                logger.warning(f"Paragraph formatting failed: {e}")
                p = Paragraph(para.replace('<', '').replace('>', ''), self.styles['FormalBody'])
                elements.append(p)

        return elements

    def _create_formal_footer(self, document_data: Dict) -> list:
        """Create footer section for formal document"""
        elements = []

        elements.append(Spacer(1, 0.5 * inch))

        # Add ending horizontal line
        from reportlab.platypus import HRFlowable
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#cccccc'),
            spaceBefore=20
        ))

        # End note
        elements.append(Spacer(1, 0.2 * inch))
        footer_text = "— End of Document —"
        footer_para = Paragraph(footer_text, self.styles['FormalFooter'])
        elements.append(footer_para)

        return elements

    def _add_edge_decorations(self, canvas, doc, color_scheme: List[str]):
        """Add decorative vertical lines on the right edge of pages"""
        canvas.saveState()

        # Page dimensions
        page_width, page_height = letter

        # Draw 3 vertical lines on the right edge with varying thickness
        line_positions = [
            (page_width - 20, 2, color_scheme[0]),  # Outermost - thickest
            (page_width - 25, 1.5, color_scheme[1] if len(color_scheme) > 1 else color_scheme[0]),
            (page_width - 29, 1, color_scheme[2] if len(color_scheme) > 2 else color_scheme[0]),
        ]

        margin_top = 72
        margin_bottom = 72

        for x_pos, thickness, color_hex in line_positions:
            canvas.setStrokeColor(colors.HexColor(color_hex))
            canvas.setLineWidth(thickness)
            canvas.line(x_pos, margin_bottom, x_pos, page_height - margin_top)

        canvas.restoreState()