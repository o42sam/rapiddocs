from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import os
from typing import Optional
from app.utils.logger import get_logger
from app.utils.exceptions import PDFGenerationError

logger = get_logger('watermark_service')


class WatermarkService:
    """Service for adding watermarks to PDF documents"""

    def create_watermark_page(self, logo_path: str, page_width: float, page_height: float, opacity: float = 0.15) -> io.BytesIO:
        """
        Create a PDF page with just the watermark logo

        Args:
            logo_path: Path to the logo image
            page_width: Width of the page
            page_height: Height of the page
            opacity: Opacity of the watermark (0.0 to 1.0)

        Returns:
            BytesIO buffer containing the watermark PDF page
        """
        packet = io.BytesIO()

        try:
            # Create a new PDF with Reportlab
            c = canvas.Canvas(packet, pagesize=(page_width, page_height))

            # Calculate watermark size (3 inches)
            watermark_size = 3 * 72  # 3 inches in points (72 points = 1 inch)

            # Calculate center position
            x = (page_width - watermark_size) / 2
            y = (page_height - watermark_size) / 2

            # Set opacity
            c.setFillAlpha(opacity)
            c.setStrokeAlpha(opacity)

            # Draw the image
            c.drawImage(
                logo_path,
                x, y,
                width=watermark_size,
                height=watermark_size,
                preserveAspectRatio=True,
                mask='auto'
            )

            c.save()
            packet.seek(0)

            logger.debug(f"Created watermark page: size={watermark_size}pt, position=({x}, {y}), opacity={opacity}")
            return packet

        except Exception as e:
            logger.error(f"Failed to create watermark page: {str(e)}", exc_info=True)
            raise PDFGenerationError(f"Failed to create watermark: {str(e)}")

    def add_watermark_to_pdf(
        self,
        input_pdf_path: str,
        output_pdf_path: str,
        logo_path: str,
        skip_first_page: bool = True,
        opacity: float = 0.15
    ) -> str:
        """
        Add watermark to an existing PDF file

        Args:
            input_pdf_path: Path to the input PDF
            output_pdf_path: Path where watermarked PDF will be saved
            logo_path: Path to the logo image for watermark
            skip_first_page: If True, skip watermark on first page (cover)
            opacity: Opacity of the watermark (0.0 to 1.0)

        Returns:
            Path to the watermarked PDF

        Raises:
            PDFGenerationError: If watermarking fails
        """
        try:
            logger.info(f"Adding watermark to PDF: {input_pdf_path}")
            logger.info(f"Logo: {logo_path}, skip_first_page: {skip_first_page}, opacity: {opacity}")

            # Verify logo exists
            if not os.path.exists(logo_path):
                raise PDFGenerationError(f"Logo file not found: {logo_path}")

            # Read the input PDF
            reader = PdfReader(input_pdf_path)
            writer = PdfWriter()

            total_pages = len(reader.pages)
            logger.info(f"PDF has {total_pages} pages")

            # Process each page
            for page_num, page in enumerate(reader.pages):
                # Get page dimensions
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)

                # Skip watermark on first page if requested
                if skip_first_page and page_num == 0:
                    logger.debug(f"Page {page_num + 1}: Skipping watermark (cover page)")
                    writer.add_page(page)
                else:
                    logger.debug(f"Page {page_num + 1}: Adding watermark")

                    # Create watermark for this page
                    watermark_buffer = self.create_watermark_page(
                        logo_path,
                        page_width,
                        page_height,
                        opacity
                    )

                    # Read the watermark PDF
                    watermark_reader = PdfReader(watermark_buffer)
                    watermark_page = watermark_reader.pages[0]

                    # Merge watermark with the page
                    page.merge_page(watermark_page)
                    writer.add_page(page)

            # Write the output PDF
            with open(output_pdf_path, 'wb') as output_file:
                writer.write(output_file)

            logger.info(f"Watermarked PDF created successfully: {output_pdf_path}")
            return output_pdf_path

        except PDFGenerationError:
            raise
        except Exception as e:
            logger.error(f"Failed to add watermark to PDF: {str(e)}", exc_info=True)
            raise PDFGenerationError(f"Watermark operation failed: {str(e)}")


watermark_service = WatermarkService()
