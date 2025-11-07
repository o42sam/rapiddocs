from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors as rl_colors
from reportlab.pdfgen import canvas
from datetime import datetime
import os
from typing import List, Tuple, Optional
from app.models.document import DesignSpecification
from app.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import PDFGenerationError

logger = get_logger('pdf_generator')


class PDFGeneratorService:
    def __init__(self):
        self.page_width, self.page_height = letter
        self.margin = 1 * inch
        self.header_counter = 0  # Track header alternation

    def _hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB tuple (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    def _create_color(self, hex_color: str):
        """Create ReportLab color from hex"""
        r, g, b = self._hex_to_rgb(hex_color)
        return rl_colors.Color(r, g, b)

    def _draw_page_decorations(self, canvas_obj, doc, design_spec: DesignSpecification, document_type: str = "infographic", use_watermark: bool = False, logo_path: Optional[str] = None, is_cover: bool = False):
        """
        Draw decorative elements on pages based on document type

        For FORMAL documents: 3 vertical lines of varying thickness on the right edge,
                             alternating between foreground colors
        For INFOGRAPHIC documents: No edge decorations

        Watermark: Only added for formal documents when use_watermark=True and logo exists
        """
        canvas_obj.saveState()

        # Only draw edge decorations for FORMAL documents
        if document_type == "formal":
            logger.debug("Drawing formal document edge decorations")

            # Get both foreground colors
            r1, g1, b1 = self._hex_to_rgb(design_spec.foreground_color_1)
            r2, g2, b2 = self._hex_to_rgb(design_spec.foreground_color_2)

            # Define line properties: (x_position, thickness, color_rgb)
            # Three lines with varying thickness, alternating colors
            lines = [
                (self.page_width - 0.15*inch, 3, (r1, g1, b1)),   # Line 1: thin, color1
                (self.page_width - 0.35*inch, 6, (r2, g2, b2)),   # Line 2: medium, color2
                (self.page_width - 0.60*inch, 4, (r1, g1, b1))    # Line 3: thin-medium, color1
            ]

            # Draw each line
            for x_pos, thickness, (r, g, b) in lines:
                canvas_obj.setStrokeColorRGB(r, g, b)
                canvas_obj.setLineWidth(thickness)

                # Draw vertical line from top to bottom of page
                canvas_obj.line(x_pos, 0, x_pos, self.page_height)

                logger.debug(f"Drew line at x={x_pos}, thickness={thickness}")

        elif document_type == "infographic":
            logger.debug("Infographic document - skipping edge decorations")

        # Add logo watermark (only on non-cover pages, only for formal documents when use_watermark is True)
        if use_watermark and document_type == "formal" and logo_path and os.path.exists(logo_path) and not is_cover:
            try:
                # Draw logo as watermark in center with transparency
                logo_width = 3 * inch
                logo_height = 3 * inch
                x = (self.page_width - logo_width) / 2
                y = (self.page_height - logo_height) / 2

                # Set transparency for watermark effect (semi-transparent)
                canvas_obj.setFillAlpha(0.08)
                canvas_obj.setStrokeAlpha(0.08)

                canvas_obj.drawImage(
                    logo_path,
                    x, y,
                    width=logo_width,
                    height=logo_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                logger.debug("Added logo watermark to formal document")
            except Exception as e:
                logger.error(f"Failed to add logo watermark: {str(e)}")

        canvas_obj.restoreState()

    def _create_styles(self, design_spec: DesignSpecification):
        """Create custom styles based on design specification"""
        styles = getSampleStyleSheet()

        # Store colors for later use
        self.color1 = self._create_color(design_spec.foreground_color_1)
        self.color2 = self._create_color(design_spec.foreground_color_2)

        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=self.color1,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Heading1 style - will alternate colors
        styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=self.color1,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Heading2 style - will alternate colors
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.color2,
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))

        # Body style
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=14
        ))

        return styles

    def _add_cover_page(
        self,
        elements: List,
        title: str,
        logo_path: Optional[str],
        design_spec: DesignSpecification,
        styles
    ):
        """Add cover page to PDF"""
        # Add logo at top center if provided
        if logo_path and os.path.exists(logo_path):
            try:
                # Add small spacer from top
                elements.append(Spacer(1, 0.5*inch))

                # Add logo centered at top
                logo = Image(logo_path, width=2*inch, height=2*inch, kind='proportional')
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.5*inch))
            except:
                pass

        # Add spacer to center title vertically
        elements.append(Spacer(1, 1.5*inch))

        # Add title
        title_para = Paragraph(title, styles['CustomTitle'])
        elements.append(title_para)

        elements.append(Spacer(1, 0.5*inch))

        # Add date
        date_str = datetime.now().strftime("%B %d, %Y")
        date_para = Paragraph(f"<i>{date_str}</i>", styles['Normal'])
        date_para.alignment = TA_CENTER
        elements.append(date_para)

        # Add color accent bar
        color1 = self._create_color(design_spec.foreground_color_1)
        accent_table = Table([['']], colWidths=[6*inch], rowHeights=[0.1*inch])
        accent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), color1),
        ]))
        elements.append(Spacer(1, 1*inch))
        elements.append(accent_table)

        elements.append(PageBreak())

    def _parse_and_format_content(self, text: str, styles) -> List:
        """Parse generated text and format it with proper styles"""
        elements = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 0.1*inch))
                continue

            # Detect headings
            if line.startswith('# '):
                # H1 - Alternate between color1 and color2
                content = line[2:].strip()
                header_color = self.color1 if self.header_counter % 2 == 0 else self.color2

                # Create a custom style with the alternating color
                header_style = ParagraphStyle(
                    name=f'DynamicHeading1_{self.header_counter}',
                    parent=styles['CustomHeading1'],
                    textColor=header_color
                )

                para = Paragraph(content, header_style)
                elements.append(para)
                self.header_counter += 1

            elif line.startswith('## '):
                # H2 - Alternate between color1 and color2
                content = line[3:].strip()
                header_color = self.color1 if self.header_counter % 2 == 0 else self.color2

                # Create a custom style with the alternating color
                header_style = ParagraphStyle(
                    name=f'DynamicHeading2_{self.header_counter}',
                    parent=styles['CustomHeading2'],
                    textColor=header_color
                )

                para = Paragraph(content, header_style)
                elements.append(para)
                self.header_counter += 1

            elif line.startswith('### '):
                # H3
                content = line[4:].strip()
                para = Paragraph(f"<b>{content}</b>", styles['CustomBody'])
                elements.append(para)

            # Check if line is bold text enclosed in ** (likely a header from LLM)
            elif line.startswith('**') and line.endswith('**') and len(line) > 4:
                # Extract content without asterisks
                content = line[2:-2].strip()

                # Treat as a styled header with alternating colors
                header_color = self.color1 if self.header_counter % 2 == 0 else self.color2

                header_style = ParagraphStyle(
                    name=f'DynamicBoldHeader_{self.header_counter}',
                    parent=styles['CustomHeading2'],
                    textColor=header_color,
                    fontSize=16,
                    fontName='Helvetica-Bold'
                )

                para = Paragraph(content, header_style)
                elements.append(para)
                self.header_counter += 1

            # Check if line is a bullet point
            elif line.startswith(('- ', '* ', '• ', '◦ ')):
                # Extract content after bullet marker
                import re
                content = re.sub(r'^[-*•◦]\s+', '', line)

                # Escape XML special characters
                content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

                # Convert **text** to <b>text</b> for inline bold
                content = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', content)

                # Format as bullet point with proper indentation
                bullet_text = f"• {content}"

                # Create a custom style for bullet points with left indentation
                bullet_style = ParagraphStyle(
                    name='BulletPoint',
                    parent=styles['CustomBody'],
                    leftIndent=20,
                    spaceAfter=6,
                    leading=14
                )

                para = Paragraph(bullet_text, bullet_style)
                elements.append(para)

            else:
                # Regular paragraph - handle inline bold formatting
                # Escape XML special characters first
                line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

                # Convert **text** to <b>text</b> for inline bold
                import re
                line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)

                para = Paragraph(line, styles['CustomBody'])
                elements.append(para)

        return elements

    def _add_images(self, elements: List, image_paths: List[str]):
        """Add generated images to PDF"""
        for img_path in image_paths:
            if os.path.exists(img_path):
                try:
                    img = Image(img_path, width=5*inch, height=3*inch, kind='proportional')
                    img.hAlign = 'CENTER'
                    elements.append(Spacer(1, 0.2*inch))
                    elements.append(img)
                    elements.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    print(f"Failed to add image {img_path}: {str(e)}")

    def _add_visualizations(
        self,
        elements: List,
        visualization_paths: List[str],
        styles
    ):
        """Add data visualizations to PDF"""
        if not visualization_paths:
            return

        elements.append(PageBreak())
        elements.append(Paragraph("Company Statistics", styles['CustomHeading1']))
        elements.append(Spacer(1, 0.3*inch))

        for viz_path in visualization_paths:
            if os.path.exists(viz_path):
                try:
                    viz = Image(viz_path, width=6*inch, height=3.5*inch, kind='proportional')
                    viz.hAlign = 'CENTER'
                    elements.append(viz)
                    elements.append(Spacer(1, 0.3*inch))
                except Exception as e:
                    print(f"Failed to add visualization {viz_path}: {str(e)}")

    def generate_pdf(
        self,
        output_path: str,
        title: str,
        content: str,
        design_spec: DesignSpecification,
        document_type: str = "infographic",
        use_watermark: bool = False,
        logo_path: Optional[str] = None,
        image_paths: List[str] = [],
        visualization_paths: List[str] = []
    ) -> str:
        """
        Generate PDF document

        Args:
            output_path: Path where the PDF will be saved
            title: Document title
            content: Document text content
            design_spec: Design specifications (colors, theme)
            document_type: Type of document - "formal" or "infographic"
            use_watermark: Whether to use logo as watermark (only for formal documents with logo)
            logo_path: Optional path to company logo
            image_paths: List of paths to generated images (only used for infographic)
            visualization_paths: List of paths to visualizations (only used for infographic)

        Returns:
            Path to generated PDF

        Raises:
            PDFGenerationError: If PDF generation fails
        """
        try:
            logger.info(f"Starting PDF generation: type={document_type}, title={title}")

            # Validate document type
            if document_type not in ['formal', 'infographic']:
                raise PDFGenerationError(
                    f"Invalid document_type: {document_type}",
                    details={'valid_types': ['formal', 'infographic']}
                )

            # Reset header counter for each document
            self.header_counter = 0

            # Create PDF document with custom page template
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )

            # Create custom styles
            styles = self._create_styles(design_spec)

            # Build document elements
            elements = []

            # Add cover page
            logger.info("Adding cover page")
            self._add_cover_page(elements, title, logo_path, design_spec, styles)

            # Add main content
            logger.info("Adding main content")
            content_elements = self._parse_and_format_content(content, styles)
            elements.extend(content_elements)

            # Add generated images and visualizations ONLY for infographic type
            if document_type == "infographic":
                logger.info("Document type is infographic - adding images and visualizations")

                # Add generated images
                if image_paths:
                    logger.info(f"Adding {len(image_paths)} generated images")
                    elements.append(Spacer(1, 0.3*inch))
                    self._add_images(elements, image_paths)
                else:
                    logger.warning("No images provided for infographic document")

                # Add visualizations
                if visualization_paths:
                    logger.info(f"Adding {len(visualization_paths)} visualizations")
                    self._add_visualizations(elements, visualization_paths, styles)
                else:
                    logger.warning("No visualizations provided for infographic document")

            elif document_type == "formal":
                logger.info("Document type is formal - skipping images and visualizations")

            # Add footer note
            elements.append(PageBreak())
            footer_text = f"<i>Document generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>"
            footer = Paragraph(footer_text, styles['Normal'])
            elements.append(footer)

            # Build PDF with custom page decoration callbacks
            def add_cover_decorations(canvas_obj, doc_obj):
                self._draw_page_decorations(canvas_obj, doc_obj, design_spec, document_type=document_type, use_watermark=use_watermark, logo_path=logo_path, is_cover=True)

            def add_page_decorations(canvas_obj, doc_obj):
                self._draw_page_decorations(canvas_obj, doc_obj, design_spec, document_type=document_type, use_watermark=use_watermark, logo_path=logo_path, is_cover=False)

            logger.info("Building PDF document")
            doc.build(elements, onFirstPage=add_cover_decorations, onLaterPages=add_page_decorations)

            logger.info(f"PDF generated successfully: {output_path}")
            return output_path

        except PDFGenerationError:
            raise
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
            raise PDFGenerationError(
                f"Failed to generate PDF: {str(e)}",
                details={'output_path': output_path, 'title': title}
            )


pdf_generator_service = PDFGeneratorService()
