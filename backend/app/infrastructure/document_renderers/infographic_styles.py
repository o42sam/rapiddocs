"""
Infographic Document Styles.
Defines styling constants and configurations for infographic PDFs.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from reportlab.lib import colors
from reportlab.lib.units import inch


@dataclass
class InfographicColorScheme:
    """Color scheme for infographic documents."""
    primary: str = "#1e40af"
    secondary: str = "#3730a3"
    tertiary: str = "#7c3aed"
    accent: str = "#f59e0b"
    text_dark: str = "#1f2937"
    text_light: str = "#6b7280"
    background: str = "#ffffff"
    cover_gradient_start: str = "#1e3a5f"
    cover_gradient_end: str = "#3b82f6"

    def to_reportlab_colors(self) -> Dict[str, colors.Color]:
        """Convert hex colors to ReportLab Color objects."""
        return {
            "primary": self._hex_to_color(self.primary),
            "secondary": self._hex_to_color(self.secondary),
            "tertiary": self._hex_to_color(self.tertiary),
            "accent": self._hex_to_color(self.accent),
            "text_dark": self._hex_to_color(self.text_dark),
            "text_light": self._hex_to_color(self.text_light),
            "background": self._hex_to_color(self.background)
        }

    def _hex_to_color(self, hex_color: str) -> colors.Color:
        """Convert hex color to ReportLab Color."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return colors.Color(r, g, b)

    @classmethod
    def from_hex_list(cls, color_list: List[str]) -> "InfographicColorScheme":
        """Create color scheme from a list of hex colors."""
        scheme = cls()
        if len(color_list) >= 1:
            scheme.primary = color_list[0]
        if len(color_list) >= 2:
            scheme.secondary = color_list[1]
        if len(color_list) >= 3:
            scheme.tertiary = color_list[2]
        if len(color_list) >= 4:
            scheme.accent = color_list[3]
        return scheme


@dataclass
class InfographicTypography:
    """Typography settings for infographic documents."""
    # Font families
    heading_font: str = "Helvetica-Bold"
    body_font: str = "Helvetica"
    accent_font: str = "Helvetica-Oblique"

    # Font sizes
    cover_title_size: int = 36
    cover_subtitle_size: int = 18
    section_heading_size: int = 18
    subsection_heading_size: int = 14
    body_size: int = 11
    caption_size: int = 9
    footer_size: int = 8

    # Line heights (as multiplier of font size)
    heading_line_height: float = 1.3
    body_line_height: float = 1.5
    caption_line_height: float = 1.3


@dataclass
class InfographicLayout:
    """Layout settings for infographic documents."""
    # Page margins
    left_margin: float = 0.75 * inch
    right_margin: float = 0.75 * inch
    top_margin: float = 0.75 * inch
    bottom_margin: float = 0.75 * inch

    # Content spacing
    section_spacing: float = 0.5 * inch
    paragraph_spacing: float = 0.25 * inch
    image_spacing: float = 0.3 * inch

    # Image settings
    inline_image_width: float = 4.5 * inch
    inline_image_height: float = 3.0 * inch
    chart_width: float = 5.0 * inch
    chart_height: float = 3.5 * inch
    illustration_width: float = 4.0 * inch
    illustration_height: float = 2.5 * inch

    # Cover page
    logo_max_width: float = 2.0 * inch
    logo_max_height: float = 1.0 * inch
    cover_title_y_offset: float = 4.0 * inch

    # Footer
    footer_height: float = 0.5 * inch


@dataclass
class InfographicStyle:
    """Complete style configuration for infographic documents."""
    colors: InfographicColorScheme = field(default_factory=InfographicColorScheme)
    typography: InfographicTypography = field(default_factory=InfographicTypography)
    layout: InfographicLayout = field(default_factory=InfographicLayout)

    # Additional styling options
    show_page_numbers: bool = True
    show_header: bool = True
    show_decorative_elements: bool = True

    @classmethod
    def create_with_colors(cls, color_list: List[str]) -> "InfographicStyle":
        """Create style with custom colors."""
        style = cls()
        style.colors = InfographicColorScheme.from_hex_list(color_list)
        return style


# Predefined style presets
STYLE_PRESETS: Dict[str, InfographicStyle] = {
    "professional": InfographicStyle(
        colors=InfographicColorScheme(
            primary="#1e40af",
            secondary="#3b82f6",
            tertiary="#60a5fa",
            accent="#f59e0b"
        )
    ),
    "modern": InfographicStyle(
        colors=InfographicColorScheme(
            primary="#6366f1",
            secondary="#8b5cf6",
            tertiary="#a78bfa",
            accent="#ec4899"
        )
    ),
    "corporate": InfographicStyle(
        colors=InfographicColorScheme(
            primary="#1e3a5f",
            secondary="#2563eb",
            tertiary="#64748b",
            accent="#0891b2"
        )
    ),
    "nature": InfographicStyle(
        colors=InfographicColorScheme(
            primary="#166534",
            secondary="#22c55e",
            tertiary="#4ade80",
            accent="#ca8a04"
        )
    ),
    "warm": InfographicStyle(
        colors=InfographicColorScheme(
            primary="#dc2626",
            secondary="#f97316",
            tertiary="#fbbf24",
            accent="#7c3aed"
        )
    )
}


def get_style_preset(name: str = "professional") -> InfographicStyle:
    """
    Get a predefined style preset.

    Args:
        name: Preset name (professional, modern, corporate, nature, warm)

    Returns:
        InfographicStyle instance
    """
    return STYLE_PRESETS.get(name.lower(), STYLE_PRESETS["professional"])
