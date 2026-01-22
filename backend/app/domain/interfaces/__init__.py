"""
Domain interfaces (contracts).
All infrastructure implementations must implement these interfaces.
"""

from .text_generator import ITextGenerator
from .image_generator import IImageGenerator
from .document_renderer import IDocumentRenderer
from .visualization_engine import IVisualizationEngine
from .table_generator import ITableGenerator
from .watermark_service import IWatermarkService
from .redaction_service import IRedactionService
from .data_importer import IDataImporter
from .document_repository import IDocumentRepository

__all__ = [
    "ITextGenerator",
    "IImageGenerator",
    "IDocumentRenderer",
    "IVisualizationEngine",
    "ITableGenerator",
    "IWatermarkService",
    "IRedactionService",
    "IDataImporter",
    "IDocumentRepository"
]