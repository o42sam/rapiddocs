"""
Watermark Configuration Value Object.
Represents watermark settings for documents.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class WatermarkPosition(Enum):
    """Supported watermark positions."""
    CENTER = "center"
    DIAGONAL = "diagonal"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


class WatermarkType(Enum):
    """Types of watermarks."""
    IMAGE = "image"
    TEXT = "text"


@dataclass(frozen=True)
class WatermarkConfig:
    """
    Immutable value object representing watermark configuration.

    Attributes:
        watermark_type: Type of watermark (image or text)
        opacity: Watermark opacity (0.0-1.0)
        position: Position of the watermark on the page
        size_inches: Size of the watermark in inches
        skip_first_page: Whether to skip watermark on the first page
        rotation: Rotation angle for diagonal text watermarks
        font_size: Font size for text watermarks
        font_color: Color for text watermarks (hex code)
    """
    watermark_type: WatermarkType
    opacity: float = 0.15
    position: WatermarkPosition = WatermarkPosition.CENTER
    size_inches: float = 3.0
    skip_first_page: bool = True
    rotation: float = 0.0  # For diagonal text watermarks
    font_size: int = 48    # For text watermarks
    font_color: str = "#000000"  # For text watermarks

    def __post_init__(self):
        """Validate watermark configuration."""
        if not 0.0 <= self.opacity <= 1.0:
            raise ValueError("Opacity must be between 0.0 and 1.0")
        if self.size_inches <= 0:
            raise ValueError("Size must be positive")
        if self.font_size <= 0:
            raise ValueError("Font size must be positive")
        if not self.font_color.startswith("#"):
            raise ValueError("Font color must be a hex color code")

    @classmethod
    def image_watermark(
        cls,
        opacity: float = 0.15,
        position: WatermarkPosition = WatermarkPosition.CENTER,
        size_inches: float = 3.0,
        skip_first_page: bool = True
    ) -> "WatermarkConfig":
        """Create an image watermark configuration."""
        return cls(
            watermark_type=WatermarkType.IMAGE,
            opacity=opacity,
            position=position,
            size_inches=size_inches,
            skip_first_page=skip_first_page
        )

    @classmethod
    def text_watermark(
        cls,
        opacity: float = 0.15,
        position: WatermarkPosition = WatermarkPosition.CENTER,
        font_size: int = 48,
        font_color: str = "#000000",
        rotation: float = 0.0,
        skip_first_page: bool = True
    ) -> "WatermarkConfig":
        """Create a text watermark configuration."""
        return cls(
            watermark_type=WatermarkType.TEXT,
            opacity=opacity,
            position=position,
            font_size=font_size,
            font_color=font_color,
            rotation=rotation,
            skip_first_page=skip_first_page
        )