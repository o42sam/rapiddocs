"""
Chart Styles Configuration.
Defines color schemes and styling for visualizations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from enum import Enum


class ColorScheme(Enum):
    """Predefined color schemes for charts."""
    BLUE = "blue"
    GREEN = "green"
    PURPLE = "purple"
    ORANGE = "orange"
    RED = "red"
    TEAL = "teal"
    CORPORATE = "corporate"
    MODERN = "modern"


@dataclass
class ChartColors:
    """Color configuration for a chart."""
    primary: str
    secondary: str
    tertiary: str
    accent: str
    text: str
    background: str
    grid: str

    def to_list(self) -> List[str]:
        """Get colors as a list for chart series."""
        return [self.primary, self.secondary, self.tertiary, self.accent]


# Predefined color palettes
COLOR_PALETTES: Dict[ColorScheme, ChartColors] = {
    ColorScheme.BLUE: ChartColors(
        primary="#1e40af",
        secondary="#3b82f6",
        tertiary="#60a5fa",
        accent="#93c5fd",
        text="#1f2937",
        background="#ffffff",
        grid="#e5e7eb"
    ),
    ColorScheme.GREEN: ChartColors(
        primary="#166534",
        secondary="#22c55e",
        tertiary="#4ade80",
        accent="#86efac",
        text="#1f2937",
        background="#ffffff",
        grid="#e5e7eb"
    ),
    ColorScheme.PURPLE: ChartColors(
        primary="#7c3aed",
        secondary="#8b5cf6",
        tertiary="#a78bfa",
        accent="#c4b5fd",
        text="#1f2937",
        background="#ffffff",
        grid="#e5e7eb"
    ),
    ColorScheme.ORANGE: ChartColors(
        primary="#ea580c",
        secondary="#f97316",
        tertiary="#fb923c",
        accent="#fdba74",
        text="#1f2937",
        background="#ffffff",
        grid="#e5e7eb"
    ),
    ColorScheme.RED: ChartColors(
        primary="#dc2626",
        secondary="#ef4444",
        tertiary="#f87171",
        accent="#fca5a5",
        text="#1f2937",
        background="#ffffff",
        grid="#e5e7eb"
    ),
    ColorScheme.TEAL: ChartColors(
        primary="#0d9488",
        secondary="#14b8a6",
        tertiary="#2dd4bf",
        accent="#5eead4",
        text="#1f2937",
        background="#ffffff",
        grid="#e5e7eb"
    ),
    ColorScheme.CORPORATE: ChartColors(
        primary="#1e3a5f",
        secondary="#2563eb",
        tertiary="#64748b",
        accent="#94a3b8",
        text="#1e293b",
        background="#ffffff",
        grid="#e2e8f0"
    ),
    ColorScheme.MODERN: ChartColors(
        primary="#6366f1",
        secondary="#ec4899",
        tertiary="#14b8a6",
        accent="#f59e0b",
        text="#1f2937",
        background="#ffffff",
        grid="#e5e7eb"
    )
}


@dataclass
class ChartStyle:
    """Style configuration for charts."""
    # Figure settings
    figure_width: float = 10.0
    figure_height: float = 6.0
    figure_dpi: int = 150

    # Font settings
    title_fontsize: int = 16
    label_fontsize: int = 12
    tick_fontsize: int = 10
    legend_fontsize: int = 10
    font_family: str = "sans-serif"

    # Spacing
    title_pad: int = 20
    label_pad: int = 10

    # Grid settings
    show_grid: bool = True
    grid_alpha: float = 0.3
    grid_linestyle: str = "-"

    # Legend settings
    show_legend: bool = True
    legend_location: str = "best"

    # Bar chart specific
    bar_width: float = 0.6
    bar_edge_width: float = 0.5

    # Pie chart specific
    pie_start_angle: int = 90
    pie_explode_factor: float = 0.02

    # Line chart specific
    line_width: float = 2.5
    marker_size: int = 8
    marker_style: str = "o"

    # Gauge chart specific
    gauge_thickness: float = 0.3


class ChartStyleManager:
    """
    Manages chart styles and color schemes.
    """

    def __init__(self, scheme: ColorScheme = ColorScheme.BLUE):
        """
        Initialize style manager with a color scheme.

        Args:
            scheme: The color scheme to use
        """
        self._scheme = scheme
        self._colors = COLOR_PALETTES.get(scheme, COLOR_PALETTES[ColorScheme.BLUE])
        self._style = ChartStyle()

    @property
    def colors(self) -> ChartColors:
        """Get current color configuration."""
        return self._colors

    @property
    def style(self) -> ChartStyle:
        """Get current style configuration."""
        return self._style

    def set_scheme(self, scheme: ColorScheme) -> None:
        """Set the color scheme."""
        self._scheme = scheme
        self._colors = COLOR_PALETTES.get(scheme, COLOR_PALETTES[ColorScheme.BLUE])

    def set_colors_from_hex(self, colors: List[str]) -> None:
        """
        Set colors from a list of hex color codes.

        Args:
            colors: List of hex color codes (at least 2)
        """
        if len(colors) >= 4:
            self._colors = ChartColors(
                primary=colors[0],
                secondary=colors[1],
                tertiary=colors[2],
                accent=colors[3] if len(colors) > 3 else colors[2],
                text="#1f2937",
                background="#ffffff",
                grid="#e5e7eb"
            )
        elif len(colors) >= 2:
            # Generate shades from available colors
            self._colors = ChartColors(
                primary=colors[0],
                secondary=colors[1],
                tertiary=colors[0],
                accent=colors[1],
                text="#1f2937",
                background="#ffffff",
                grid="#e5e7eb"
            )
        elif len(colors) == 1:
            # Use single color with variations
            base = colors[0]
            self._colors = ChartColors(
                primary=base,
                secondary=self._lighten_color(base, 0.2),
                tertiary=self._lighten_color(base, 0.4),
                accent=self._lighten_color(base, 0.6),
                text="#1f2937",
                background="#ffffff",
                grid="#e5e7eb"
            )

    def get_color_list(self, count: int = 4) -> List[str]:
        """
        Get a list of colors for chart series.

        Args:
            count: Number of colors needed

        Returns:
            List of hex color codes
        """
        base_colors = self._colors.to_list()

        if count <= len(base_colors):
            return base_colors[:count]

        # Generate additional colors by lightening existing ones
        extended = base_colors.copy()
        while len(extended) < count:
            for color in base_colors:
                if len(extended) >= count:
                    break
                extended.append(self._lighten_color(color, 0.3))

        return extended[:count]

    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """
        Lighten a hex color by a factor.

        Args:
            hex_color: Hex color code (e.g., "#1e40af")
            factor: Lightening factor (0.0 to 1.0)

        Returns:
            Lightened hex color
        """
        # Remove # if present
        hex_color = hex_color.lstrip('#')

        # Parse RGB values
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Lighten each component
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)

        # Ensure values are in valid range
        r = min(255, max(0, r))
        g = min(255, max(0, g))
        b = min(255, max(0, b))

        return f"#{r:02x}{g:02x}{b:02x}"

    def _darken_color(self, hex_color: str, factor: float) -> str:
        """
        Darken a hex color by a factor.

        Args:
            hex_color: Hex color code
            factor: Darkening factor (0.0 to 1.0)

        Returns:
            Darkened hex color
        """
        hex_color = hex_color.lstrip('#')

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))

        r = min(255, max(0, r))
        g = min(255, max(0, g))
        b = min(255, max(0, b))

        return f"#{r:02x}{g:02x}{b:02x}"

    def get_matplotlib_style(self) -> Dict[str, Any]:
        """
        Get matplotlib rcParams style dictionary.

        Returns:
            Dictionary of matplotlib style parameters
        """
        return {
            'figure.figsize': (self._style.figure_width, self._style.figure_height),
            'figure.dpi': self._style.figure_dpi,
            'font.family': self._style.font_family,
            'font.size': self._style.label_fontsize,
            'axes.titlesize': self._style.title_fontsize,
            'axes.labelsize': self._style.label_fontsize,
            'xtick.labelsize': self._style.tick_fontsize,
            'ytick.labelsize': self._style.tick_fontsize,
            'legend.fontsize': self._style.legend_fontsize,
            'axes.grid': self._style.show_grid,
            'grid.alpha': self._style.grid_alpha,
            'grid.linestyle': self._style.grid_linestyle,
            'axes.facecolor': self._colors.background,
            'figure.facecolor': self._colors.background,
            'text.color': self._colors.text,
            'axes.labelcolor': self._colors.text,
            'xtick.color': self._colors.text,
            'ytick.color': self._colors.text,
            'axes.edgecolor': self._colors.grid,
            'grid.color': self._colors.grid,
        }
