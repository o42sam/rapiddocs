"""
Domain value objects.
Immutable objects that have no identity.
"""

from .document_format import DocumentFormat, OutputFormat
from .watermark_config import WatermarkConfig, WatermarkPosition, WatermarkType
from .design_spec import DesignSpec
from .statistic import Statistic

__all__ = [
    "DocumentFormat",
    "OutputFormat",
    "WatermarkConfig",
    "WatermarkPosition",
    "WatermarkType",
    "DesignSpec",
    "Statistic"
]