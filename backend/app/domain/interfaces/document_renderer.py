"""
Document Renderer Interface.
Defines the contract for document rendering implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path


class IDocumentRenderer(ABC):
    """
    Interface for document rendering.
    Implementations: PDF (ReportLab), DOCX (python-docx), HTML, Markdown
    """

    @abstractmethod
    async def render(
        self,
        content: Dict[str, Any],
        output_path: Path,
        format: str
    ) -> Path:
        """
        Render document to specified format.

        Args:
            content: Document content dictionary
            output_path: Path to save the document
            format: Output format (pdf, docx, html, md)

        Returns:
            Path to the rendered document
        """
        pass

    @abstractmethod
    def add_text(self, text: str, style: Optional[Dict] = None) -> None:
        """
        Add text content to document.

        Args:
            text: Text content to add
            style: Optional style dictionary
        """
        pass

    @abstractmethod
    def add_image(
        self,
        image_path: Path,
        width: Optional[float] = None,
        height: Optional[float] = None,
        caption: Optional[str] = None
    ) -> None:
        """
        Add image to document.

        Args:
            image_path: Path to the image file
            width: Optional image width
            height: Optional image height
            caption: Optional image caption
        """
        pass

    @abstractmethod
    def add_table(
        self,
        data: List[List[Any]],
        headers: Optional[List[str]] = None,
        style: Optional[Dict] = None
    ) -> None:
        """
        Add table to document.

        Args:
            data: Table data as list of rows
            headers: Optional header row
            style: Optional style dictionary
        """
        pass

    @abstractmethod
    def add_page_break(self) -> None:
        """Add page break to document."""
        pass

    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Return list of supported output formats."""
        pass