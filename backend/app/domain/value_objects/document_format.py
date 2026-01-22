"""
Document Format Value Object.
Represents the output format configuration for documents.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class OutputFormat(Enum):
    """Supported document output formats."""
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "md"
    RTF = "rtf"


@dataclass(frozen=True)
class DocumentFormat:
    """
    Immutable value object representing document format configuration.

    Attributes:
        format: The output format type
        dpi: Dots per inch for image resolution
        compression: Whether to compress the output
        embed_fonts: Whether to embed fonts in the document
    """
    format: OutputFormat
    dpi: int = 300
    compression: bool = True
    embed_fonts: bool = True

    @classmethod
    def pdf(cls, dpi: int = 300) -> "DocumentFormat":
        """Create a PDF format configuration."""
        return cls(format=OutputFormat.PDF, dpi=dpi)

    @classmethod
    def docx(cls) -> "DocumentFormat":
        """Create a DOCX format configuration."""
        return cls(format=OutputFormat.DOCX)

    @classmethod
    def html(cls) -> "DocumentFormat":
        """Create an HTML format configuration."""
        return cls(format=OutputFormat.HTML)

    @classmethod
    def markdown(cls) -> "DocumentFormat":
        """Create a Markdown format configuration."""
        return cls(format=OutputFormat.MARKDOWN)

    @classmethod
    def rtf(cls) -> "DocumentFormat":
        """Create an RTF format configuration."""
        return cls(format=OutputFormat.RTF)

    def __str__(self) -> str:
        """String representation of the format."""
        return self.format.value

    @property
    def extension(self) -> str:
        """Get file extension for the format."""
        return self.format.value