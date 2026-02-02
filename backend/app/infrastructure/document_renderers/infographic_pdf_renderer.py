"""
Infographic PDF Renderer Implementation.
Generates professional infographic PDF documents using ReportLab.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import os

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    PageBreak, Table, TableStyle, KeepTogether, Flowable
)
from reportlab.pdfgen import canvas
from PIL import Image

from .infographic_styles import InfographicStyle, InfographicColorScheme, get_style_preset
from ...shared.logger import get_logger

logger = get_logger("infographic_pdf_renderer")


class ColoredLine(Flowable):
    """A colored horizontal line flowable."""

    def __init__(self, width, height=2, color='#1e40af'):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color

    def draw(self):
        self.canv.setStrokeColor(self._hex_to_color(self.color))
        self.canv.setLineWidth(self.height)
        self.canv.line(0, 0, self.width, 0)

    def _hex_to_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return colors.Color(r, g, b)


class InfographicPDFRenderer:
    """
    Renders infographic documents to PDF format using ReportLab.
    Creates professional documents with text, charts, and illustrations.

    Features:
    - Cover page with logo and title
    - Numbered sections (no bullet points)
    - Inline charts and visualizations
    - Illustrations at end of paragraphs
    - Page numbers and headers
    - Professional styling
    """

    def __init__(self, style: Optional[InfographicStyle] = None):
        """
        Initialize the infographic PDF renderer.

        Args:
            style: Optional style configuration
        """
        self._style = style or get_style_preset("professional")
        self._page_width, self._page_height = letter
        self._styles = self._create_paragraph_styles()

        logger.info("Infographic PDF Renderer initialized")
        logger.info(f"Page size: {self._page_width}x{self._page_height}")

    def _create_paragraph_styles(self) -> Dict[str, ParagraphStyle]:
        """Create paragraph styles for the document."""
        base_styles = getSampleStyleSheet()
        typography = self._style.typography
        color_scheme = self._style.colors

        custom_styles = {}

        # Cover title
        custom_styles['CoverTitle'] = ParagraphStyle(
            'CoverTitle',
            parent=base_styles['Heading1'],
            fontName=typography.heading_font,
            fontSize=typography.cover_title_size,
            textColor=self._hex_to_color(color_scheme.background),
            alignment=TA_CENTER,
            spaceAfter=20
        )

        # Cover subtitle
        custom_styles['CoverSubtitle'] = ParagraphStyle(
            'CoverSubtitle',
            parent=base_styles['Normal'],
            fontName=typography.body_font,
            fontSize=typography.cover_subtitle_size,
            textColor=self._hex_to_color('#e5e7eb'),
            alignment=TA_CENTER,
            spaceAfter=10
        )

        # Section heading
        custom_styles['SectionHeading'] = ParagraphStyle(
            'SectionHeading',
            parent=base_styles['Heading1'],
            fontName=typography.heading_font,
            fontSize=typography.section_heading_size,
            textColor=self._hex_to_color(color_scheme.primary),
            spaceBefore=20,
            spaceAfter=12,
            leading=typography.section_heading_size * typography.heading_line_height
        )

        # Subsection heading
        custom_styles['SubsectionHeading'] = ParagraphStyle(
            'SubsectionHeading',
            parent=base_styles['Heading2'],
            fontName=typography.heading_font,
            fontSize=typography.subsection_heading_size,
            textColor=self._hex_to_color(color_scheme.secondary),
            spaceBefore=15,
            spaceAfter=8,
            leftIndent=20
        )

        # Body text
        custom_styles['BodyText'] = ParagraphStyle(
            'BodyText',
            parent=base_styles['Normal'],
            fontName=typography.body_font,
            fontSize=typography.body_size,
            textColor=self._hex_to_color(color_scheme.text_dark),
            alignment=TA_JUSTIFY,
            spaceBefore=6,
            spaceAfter=6,
            leading=typography.body_size * typography.body_line_height
        )

        # Indented text (for sub-items)
        custom_styles['IndentedText'] = ParagraphStyle(
            'IndentedText',
            parent=custom_styles['BodyText'],
            leftIndent=25
        )

        # Double indented text (for sub-sub-items)
        custom_styles['DoubleIndentedText'] = ParagraphStyle(
            'DoubleIndentedText',
            parent=custom_styles['BodyText'],
            leftIndent=50
        )

        # Caption
        custom_styles['Caption'] = ParagraphStyle(
            'Caption',
            parent=base_styles['Normal'],
            fontName=typography.accent_font,
            fontSize=typography.caption_size,
            textColor=self._hex_to_color(color_scheme.text_light),
            alignment=TA_CENTER,
            spaceBefore=5,
            spaceAfter=15
        )

        # Statistic highlight
        custom_styles['StatHighlight'] = ParagraphStyle(
            'StatHighlight',
            parent=base_styles['Normal'],
            fontName=typography.heading_font,
            fontSize=typography.section_heading_size,
            textColor=self._hex_to_color(color_scheme.accent),
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=5
        )

        return custom_styles

    def _hex_to_color(self, hex_color: str) -> colors.Color:
        """Convert hex color to ReportLab Color."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return colors.Color(r, g, b)

    async def render(
        self,
        title: str,
        sections: List[Dict[str, Any]],
        charts: List[Path],
        illustrations: List[Path],
        output_path: Path,
        logo_path: Optional[Path] = None,
        include_cover: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Render the infographic document to PDF.

        Args:
            title: Document title
            sections: List of section dictionaries with 'heading' and 'content' keys
            charts: List of paths to chart images
            illustrations: List of paths to illustration images
            output_path: Path to save the PDF
            logo_path: Optional path to logo image
            include_cover: Whether to include a cover page
            metadata: Optional metadata (author, date, etc.)

        Returns:
            Path to the generated PDF
        """
        logger.info("=" * 50)
        logger.info("INFOGRAPHIC PDF RENDERING STARTED")
        logger.info("=" * 50)
        logger.info(f"Title: {title}")
        logger.info(f"Sections: {len(sections)}")
        logger.info(f"Charts: {len(charts)}")
        logger.info(f"Illustrations: {len(illustrations)}")
        logger.info(f"Output: {output_path}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            leftMargin=self._style.layout.left_margin,
            rightMargin=self._style.layout.right_margin,
            topMargin=self._style.layout.top_margin,
            bottomMargin=self._style.layout.bottom_margin
        )

        # Build story (content)
        story = []

        # Cover page
        if include_cover:
            cover_elements = self._create_cover_page(
                title,
                logo_path,
                metadata or {}
            )
            story.extend(cover_elements)
            story.append(PageBreak())

        # Content sections with charts and illustrations
        content_width = self._page_width - self._style.layout.left_margin - self._style.layout.right_margin

        chart_index = 0
        illustration_index = 0

        for i, section in enumerate(sections):
            section_num = i + 1

            # Section heading
            heading_text = section.get('heading', f'Section {section_num}')
            story.append(Paragraph(
                f"{section_num}. {heading_text}",
                self._styles['SectionHeading']
            ))

            # Decorative line under heading
            story.append(ColoredLine(
                content_width * 0.3,
                height=2,
                color=self._style.colors.primary
            ))
            story.append(Spacer(1, 10))

            # Section content (paragraphs)
            content = section.get('content', '')
            paragraphs = self._split_into_paragraphs(content)

            for j, para_text in enumerate(paragraphs):
                # Add paragraph
                story.append(Paragraph(para_text, self._styles['BodyText']))

                # Add chart if available and this is a good position
                if chart_index < len(charts) and j == 0:
                    chart_path = charts[chart_index]
                    if chart_path.exists():
                        story.append(Spacer(1, 15))
                        story.extend(self._add_image(
                            chart_path,
                            self._style.layout.chart_width,
                            self._style.layout.chart_height,
                            caption=f"Figure {chart_index + 1}"
                        ))
                        chart_index += 1

            # Add illustration at end of section
            if illustration_index < len(illustrations):
                illus_path = illustrations[illustration_index]
                if illus_path.exists():
                    story.append(Spacer(1, 15))
                    story.extend(self._add_image(
                        illus_path,
                        self._style.layout.illustration_width,
                        self._style.layout.illustration_height,
                        caption=f"Illustration: {heading_text}"
                    ))
                    illustration_index += 1

            # Add spacing between sections
            story.append(Spacer(1, self._style.layout.section_spacing))

        # Build document with page numbers
        doc.build(
            story,
            onFirstPage=self._add_page_elements,
            onLaterPages=self._add_page_elements
        )

        logger.info(f"PDF generated successfully: {output_path}")
        logger.info("=" * 50)

        return output_path

    def _create_cover_page(
        self,
        title: str,
        logo_path: Optional[Path],
        metadata: Dict[str, Any]
    ) -> List[Flowable]:
        """Create cover page elements."""
        elements = []
        layout = self._style.layout
        color_scheme = self._style.colors

        # Add vertical space to center content
        elements.append(Spacer(1, 2 * inch))

        # Logo (if provided)
        if logo_path and logo_path.exists():
            try:
                img = Image.open(logo_path)
                img_width, img_height = img.size
                aspect = img_width / img_height

                # Calculate dimensions to fit within max size
                if aspect > (layout.logo_max_width / layout.logo_max_height):
                    display_width = layout.logo_max_width
                    display_height = display_width / aspect
                else:
                    display_height = layout.logo_max_height
                    display_width = display_height * aspect

                logo_image = RLImage(
                    str(logo_path),
                    width=display_width,
                    height=display_height
                )
                logo_image.hAlign = 'CENTER'
                elements.append(logo_image)
                elements.append(Spacer(1, 0.5 * inch))
            except Exception as e:
                logger.warning(f"Failed to add logo: {e}")

        # Decorative line
        content_width = self._page_width - layout.left_margin - layout.right_margin
        elements.append(ColoredLine(content_width, height=3, color=color_scheme.primary))
        elements.append(Spacer(1, 0.3 * inch))

        # Title with custom background simulation using table
        title_style = ParagraphStyle(
            'CoverTitleDark',
            fontName=self._style.typography.heading_font,
            fontSize=self._style.typography.cover_title_size,
            textColor=self._hex_to_color(color_scheme.primary),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph(title, title_style))

        # Another decorative line
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(ColoredLine(content_width * 0.5, height=2, color=color_scheme.secondary))

        # Metadata (author, date)
        elements.append(Spacer(1, 1 * inch))

        author = metadata.get('author', '')
        date = metadata.get('date', datetime.now().strftime("%B %d, %Y"))

        meta_style = ParagraphStyle(
            'CoverMeta',
            fontName=self._style.typography.body_font,
            fontSize=self._style.typography.body_size,
            textColor=self._hex_to_color(color_scheme.text_light),
            alignment=TA_CENTER
        )

        if author:
            elements.append(Paragraph(f"Prepared by: {author}", meta_style))
            elements.append(Spacer(1, 10))

        elements.append(Paragraph(date, meta_style))

        return elements

    def _split_into_paragraphs(self, content: str) -> List[str]:
        """Split content into paragraphs."""
        # Split by double newlines or single newlines followed by numbers/letters
        paragraphs = []
        current_para = []

        lines = content.split('\n')
        for line in lines:
            stripped = line.strip()
            if not stripped:
                # Empty line - end of paragraph
                if current_para:
                    paragraphs.append(' '.join(current_para))
                    current_para = []
            else:
                current_para.append(stripped)

        # Don't forget the last paragraph
        if current_para:
            paragraphs.append(' '.join(current_para))

        return paragraphs if paragraphs else [content]

    def _add_image(
        self,
        image_path: Path,
        max_width: float,
        max_height: float,
        caption: Optional[str] = None
    ) -> List[Flowable]:
        """Add an image with optional caption."""
        elements = []

        try:
            # Get image dimensions
            img = Image.open(image_path)
            img_width, img_height = img.size
            aspect = img_width / img_height

            # Calculate display dimensions
            if aspect > (max_width / max_height):
                display_width = max_width
                display_height = display_width / aspect
            else:
                display_height = max_height
                display_width = display_height * aspect

            # Create ReportLab image
            rl_image = RLImage(
                str(image_path),
                width=display_width,
                height=display_height
            )
            rl_image.hAlign = 'CENTER'

            elements.append(rl_image)

            # Add caption if provided
            if caption:
                elements.append(Paragraph(caption, self._styles['Caption']))

        except Exception as e:
            logger.error(f"Failed to add image {image_path}: {e}")

        return elements

    def _add_page_elements(self, canvas: canvas.Canvas, doc) -> None:
        """Add header and footer to each page."""
        canvas.saveState()

        page_width = self._page_width
        page_height = self._page_height
        color_scheme = self._style.colors

        # Skip header/footer on first page (cover)
        if doc.page == 1:
            canvas.restoreState()
            return

        # Page number
        if self._style.show_page_numbers:
            canvas.setFont(self._style.typography.body_font, self._style.typography.footer_size)
            canvas.setFillColor(self._hex_to_color(color_scheme.text_light))
            canvas.drawCentredString(
                page_width / 2,
                0.4 * inch,
                f"Page {doc.page}"
            )

        # Decorative accent line at top
        if self._style.show_decorative_elements:
            canvas.setStrokeColor(self._hex_to_color(color_scheme.primary))
            canvas.setLineWidth(2)
            canvas.line(
                self._style.layout.left_margin,
                page_height - 0.4 * inch,
                page_width - self._style.layout.right_margin,
                page_height - 0.4 * inch
            )

        canvas.restoreState()

    def set_colors(self, colors: List[str]) -> None:
        """
        Set custom colors for the document.

        Args:
            colors: List of hex color codes
        """
        self._style.colors = InfographicColorScheme.from_hex_list(colors)
        self._styles = self._create_paragraph_styles()
        logger.info(f"Document colors updated: {colors}")

    def get_status(self) -> Dict[str, Any]:
        """Get renderer status information."""
        return {
            "renderer": "InfographicPDFRenderer",
            "page_size": "letter",
            "style_preset": "custom",
            "primary_color": self._style.colors.primary
        }
