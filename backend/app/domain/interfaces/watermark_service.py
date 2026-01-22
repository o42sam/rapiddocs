"""
Watermark Service Interface.
Defines the contract for watermark operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
from pathlib import Path


class IWatermarkService(ABC):
    """
    Interface for watermark operations.
    Implementations: PyPDF2 watermark, ReportLab overlay
    """

    @abstractmethod
    async def add_image_watermark(
        self,
        input_pdf: Path,
        output_pdf: Path,
        image_path: Path,
        opacity: float = 0.15,
        position: str = "center"
    ) -> Path:
        """
        Add image watermark to PDF.

        Args:
            input_pdf: Path to input PDF file
            output_pdf: Path for output PDF file
            image_path: Path to watermark image
            opacity: Watermark opacity (0.0-1.0)
            position: Watermark position

        Returns:
            Path to watermarked PDF
        """
        pass

    @abstractmethod
    async def add_text_watermark(
        self,
        input_pdf: Path,
        output_pdf: Path,
        text: str,
        opacity: float = 0.15,
        position: str = "center",
        font_size: int = 48
    ) -> Path:
        """
        Add text watermark to PDF.

        Args:
            input_pdf: Path to input PDF file
            output_pdf: Path for output PDF file
            text: Watermark text
            opacity: Watermark opacity (0.0-1.0)
            position: Watermark position
            font_size: Font size for text watermark

        Returns:
            Path to watermarked PDF
        """
        pass

    @abstractmethod
    async def create_watermark_page(
        self,
        content: Any,
        page_width: float,
        page_height: float,
        opacity: float
    ) -> bytes:
        """
        Create a watermark page overlay.

        Args:
            content: Watermark content (text or image)
            page_width: Page width in points
            page_height: Page height in points
            opacity: Watermark opacity

        Returns:
            Watermark page as bytes
        """
        pass