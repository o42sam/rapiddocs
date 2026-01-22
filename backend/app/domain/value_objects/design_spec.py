"""
Design Specification Value Object.
Represents design settings for documents.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class DesignSpec:
    """
    Immutable value object representing design specifications.

    Attributes:
        color_scheme: List of hex color codes for the color scheme
        font_family: Font family name
        font_size: Base font size in points
        logo_position: Position of logo (top-left, top-right, etc.)
        edge_decorations: Whether to include edge decorations
        decoration_colors: Colors for edge decorations
    """
    color_scheme: List[str]
    font_family: str = "Helvetica"
    font_size: int = 11
    logo_position: str = "top-left"
    edge_decorations: bool = False
    decoration_colors: Optional[List[str]] = None

    def __post_init__(self):
        """Validate design specification."""
        if not self.color_scheme:
            raise ValueError("Color scheme must contain at least one color")

        for color in self.color_scheme:
            if not color.startswith("#") or len(color) != 7:
                raise ValueError(f"Invalid hex color code: {color}")

        if self.font_size <= 0:
            raise ValueError("Font size must be positive")

        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
        if self.logo_position not in valid_positions:
            raise ValueError(f"Invalid logo position: {self.logo_position}")

        if self.edge_decorations and self.decoration_colors:
            for color in self.decoration_colors:
                if not color.startswith("#") or len(color) != 7:
                    raise ValueError(f"Invalid decoration color: {color}")

    @property
    def primary_color(self) -> str:
        """Get the primary color from the scheme."""
        return self.color_scheme[0]

    @property
    def secondary_color(self) -> Optional[str]:
        """Get the secondary color if available."""
        return self.color_scheme[1] if len(self.color_scheme) > 1 else None

    @property
    def accent_color(self) -> Optional[str]:
        """Get the accent color if available."""
        return self.color_scheme[2] if len(self.color_scheme) > 2 else None

    @classmethod
    def default(cls) -> "DesignSpec":
        """Create a default design specification."""
        return cls(
            color_scheme=["#1e40af", "#3730a3", "#7c3aed"],
            font_family="Helvetica",
            font_size=11,
            logo_position="top-left",
            edge_decorations=False
        )

    @classmethod
    def with_decorations(
        cls,
        color_scheme: List[str],
        decoration_colors: Optional[List[str]] = None
    ) -> "DesignSpec":
        """Create a design specification with edge decorations."""
        return cls(
            color_scheme=color_scheme,
            edge_decorations=True,
            decoration_colors=decoration_colors or color_scheme[:3]
        )