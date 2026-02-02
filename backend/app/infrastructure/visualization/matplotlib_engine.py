"""
Matplotlib Visualization Engine.
Implements IVisualizationEngine interface for chart generation.
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import numpy as np

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle
import matplotlib.patches as mpatches

from ...domain.interfaces.visualization_engine import IVisualizationEngine
from ...shared.logger import get_logger
from .chart_styles import ChartStyleManager, ColorScheme

logger = get_logger("matplotlib_engine")


class MatplotlibEngine(IVisualizationEngine):
    """
    Matplotlib implementation of visualization engine.
    Creates professional charts and graphs for infographic documents.

    Features:
    - Bar charts (horizontal and vertical)
    - Line charts with markers
    - Pie/donut charts
    - Gauge charts
    - Consistent styling across all chart types
    """

    def __init__(self, style_manager: Optional[ChartStyleManager] = None):
        """
        Initialize the matplotlib engine.

        Args:
            style_manager: Optional style manager, creates default if not provided
        """
        self._style_manager = style_manager or ChartStyleManager(ColorScheme.BLUE)
        self._is_active = True

        logger.info("=" * 50)
        logger.info("MATPLOTLIB VISUALIZATION ENGINE INITIALIZED")
        logger.info("=" * 50)
        logger.info(f"Backend: {matplotlib.get_backend()}")
        logger.info(f"Matplotlib version: {matplotlib.__version__}")
        logger.info("ENGINE STATUS: ACTIVE")
        logger.info("=" * 50)

    @property
    def is_active(self) -> bool:
        """Check if the engine is active."""
        return self._is_active

    def set_colors(self, colors: List[str]) -> None:
        """
        Set custom colors for charts.

        Args:
            colors: List of hex color codes
        """
        self._style_manager.set_colors_from_hex(colors)
        logger.info(f"Chart colors updated: {colors}")

    async def create_bar_chart(
        self,
        data: Dict[str, float],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """
        Create a bar chart.

        Args:
            data: Dictionary of labels to values
            title: Chart title
            colors: List of color hex codes
            output_path: Path to save the chart

        Returns:
            Path to the saved chart
        """
        logger.info(f"Creating bar chart: {title}")
        logger.debug(f"Data points: {len(data)}")

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._create_bar_chart_sync,
            data, title, colors, output_path
        )

    def _create_bar_chart_sync(
        self,
        data: Dict[str, float],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """Synchronous bar chart creation."""
        try:
            # Update colors
            if colors:
                self._style_manager.set_colors_from_hex(colors)

            style = self._style_manager.style
            chart_colors = self._style_manager.get_color_list(len(data))

            # Create figure
            fig, ax = plt.subplots(figsize=(style.figure_width, style.figure_height))

            labels = list(data.keys())
            values = list(data.values())

            # Create horizontal bars for better label readability
            y_pos = np.arange(len(labels))
            bars = ax.barh(
                y_pos,
                values,
                height=style.bar_width,
                color=chart_colors[:len(labels)],
                edgecolor='white',
                linewidth=style.bar_edge_width
            )

            # Add value labels on bars
            for bar, value in zip(bars, values):
                width = bar.get_width()
                label_x = width + max(values) * 0.02
                ax.text(
                    label_x,
                    bar.get_y() + bar.get_height() / 2,
                    f'{value:,.1f}',
                    va='center',
                    fontsize=style.tick_fontsize,
                    color=self._style_manager.colors.text
                )

            # Customize axes
            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels)
            ax.set_xlabel('Value', fontsize=style.label_fontsize)
            ax.set_title(title, fontsize=style.title_fontsize, pad=style.title_pad, fontweight='bold')

            # Style adjustments
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self._style_manager.colors.grid)
            ax.spines['bottom'].set_color(self._style_manager.colors.grid)

            # Add subtle grid
            ax.xaxis.grid(True, alpha=style.grid_alpha, linestyle=style.grid_linestyle)

            plt.tight_layout()

            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save figure
            plt.savefig(
                output_path,
                dpi=style.figure_dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            plt.close(fig)

            logger.info(f"Bar chart saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to create bar chart: {e}")
            plt.close('all')
            raise

    async def create_line_chart(
        self,
        data: Dict[str, List[float]],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """
        Create a line chart.

        Args:
            data: Dictionary of series names to value lists
            title: Chart title
            colors: List of color hex codes
            output_path: Path to save the chart

        Returns:
            Path to the saved chart
        """
        logger.info(f"Creating line chart: {title}")
        logger.debug(f"Series count: {len(data)}")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._create_line_chart_sync,
            data, title, colors, output_path
        )

    def _create_line_chart_sync(
        self,
        data: Dict[str, List[float]],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """Synchronous line chart creation."""
        try:
            if colors:
                self._style_manager.set_colors_from_hex(colors)

            style = self._style_manager.style
            chart_colors = self._style_manager.get_color_list(len(data))

            fig, ax = plt.subplots(figsize=(style.figure_width, style.figure_height))

            for i, (label, values) in enumerate(data.items()):
                x = np.arange(len(values))
                color = chart_colors[i % len(chart_colors)]

                ax.plot(
                    x,
                    values,
                    label=label,
                    color=color,
                    linewidth=style.line_width,
                    marker=style.marker_style,
                    markersize=style.marker_size,
                    markerfacecolor='white',
                    markeredgecolor=color,
                    markeredgewidth=2
                )

            # Customize axes
            ax.set_xlabel('Period', fontsize=style.label_fontsize)
            ax.set_ylabel('Value', fontsize=style.label_fontsize)
            ax.set_title(title, fontsize=style.title_fontsize, pad=style.title_pad, fontweight='bold')

            # Style adjustments
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # Grid
            ax.grid(True, alpha=style.grid_alpha, linestyle=style.grid_linestyle)

            # Legend
            if style.show_legend and len(data) > 1:
                ax.legend(loc=style.legend_location, framealpha=0.9)

            plt.tight_layout()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(
                output_path,
                dpi=style.figure_dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            plt.close(fig)

            logger.info(f"Line chart saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to create line chart: {e}")
            plt.close('all')
            raise

    async def create_pie_chart(
        self,
        data: Dict[str, float],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """
        Create a pie chart.

        Args:
            data: Dictionary of labels to values
            title: Chart title
            colors: List of color hex codes
            output_path: Path to save the chart

        Returns:
            Path to the saved chart
        """
        logger.info(f"Creating pie chart: {title}")
        logger.debug(f"Segments: {len(data)}")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._create_pie_chart_sync,
            data, title, colors, output_path
        )

    def _create_pie_chart_sync(
        self,
        data: Dict[str, float],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """Synchronous pie chart creation."""
        try:
            if colors:
                self._style_manager.set_colors_from_hex(colors)

            style = self._style_manager.style
            chart_colors = self._style_manager.get_color_list(len(data))

            fig, ax = plt.subplots(figsize=(style.figure_width, style.figure_height))

            labels = list(data.keys())
            values = list(data.values())

            # Create explode effect for first segment
            explode = [style.pie_explode_factor] * len(values)
            explode[0] = style.pie_explode_factor * 2

            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                colors=chart_colors[:len(values)],
                explode=explode,
                autopct='%1.1f%%',
                startangle=style.pie_start_angle,
                shadow=False,
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )

            # Style the percentage labels
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(style.tick_fontsize)

            # Style the labels
            for text in texts:
                text.set_fontsize(style.label_fontsize)

            ax.set_title(title, fontsize=style.title_fontsize, pad=style.title_pad, fontweight='bold')

            # Equal aspect ratio ensures circular pie
            ax.axis('equal')

            plt.tight_layout()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(
                output_path,
                dpi=style.figure_dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            plt.close(fig)

            logger.info(f"Pie chart saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to create pie chart: {e}")
            plt.close('all')
            raise

    async def create_gauge_chart(
        self,
        value: float,
        max_value: float,
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """
        Create a gauge chart.

        Args:
            value: Current value
            max_value: Maximum value for scale
            title: Chart title
            colors: List of color hex codes
            output_path: Path to save the chart

        Returns:
            Path to the saved chart
        """
        logger.info(f"Creating gauge chart: {title}")
        logger.debug(f"Value: {value} / {max_value}")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._create_gauge_chart_sync,
            value, max_value, title, colors, output_path
        )

    def _create_gauge_chart_sync(
        self,
        value: float,
        max_value: float,
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """Synchronous gauge chart creation."""
        try:
            if colors:
                self._style_manager.set_colors_from_hex(colors)

            style = self._style_manager.style

            fig, ax = plt.subplots(figsize=(8, 5))

            # Calculate percentage
            percentage = min(value / max_value, 1.0) if max_value > 0 else 0

            # Gauge parameters
            center = (0.5, 0.3)
            radius = 0.4
            thickness = style.gauge_thickness

            # Background arc (gray)
            background = Wedge(
                center,
                radius,
                180,
                0,
                width=thickness,
                facecolor='#e5e7eb',
                edgecolor='white',
                linewidth=2
            )
            ax.add_patch(background)

            # Calculate end angle based on percentage
            end_angle = 180 - (percentage * 180)

            # Determine color based on value
            if percentage < 0.33:
                gauge_color = self._style_manager.colors.accent
            elif percentage < 0.66:
                gauge_color = self._style_manager.colors.secondary
            else:
                gauge_color = self._style_manager.colors.primary

            if colors and len(colors) > 0:
                gauge_color = colors[0]

            # Value arc
            value_wedge = Wedge(
                center,
                radius,
                180,
                end_angle,
                width=thickness,
                facecolor=gauge_color,
                edgecolor='white',
                linewidth=2
            )
            ax.add_patch(value_wedge)

            # Center circle
            inner_circle = Circle(
                center,
                radius - thickness - 0.02,
                facecolor='white',
                edgecolor='#e5e7eb',
                linewidth=2
            )
            ax.add_patch(inner_circle)

            # Value text
            ax.text(
                center[0],
                center[1] + 0.05,
                f'{value:,.1f}',
                ha='center',
                va='center',
                fontsize=28,
                fontweight='bold',
                color=self._style_manager.colors.text
            )

            # Percentage text
            ax.text(
                center[0],
                center[1] - 0.08,
                f'{percentage * 100:.0f}%',
                ha='center',
                va='center',
                fontsize=14,
                color=self._style_manager.colors.text
            )

            # Title
            ax.text(
                center[0],
                0.85,
                title,
                ha='center',
                va='center',
                fontsize=style.title_fontsize,
                fontweight='bold',
                color=self._style_manager.colors.text
            )

            # Min and Max labels
            ax.text(
                center[0] - radius - 0.05,
                center[1] - 0.15,
                '0',
                ha='center',
                va='center',
                fontsize=style.tick_fontsize,
                color=self._style_manager.colors.text
            )

            ax.text(
                center[0] + radius + 0.05,
                center[1] - 0.15,
                f'{max_value:,.0f}',
                ha='center',
                va='center',
                fontsize=style.tick_fontsize,
                color=self._style_manager.colors.text
            )

            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            plt.tight_layout()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(
                output_path,
                dpi=style.figure_dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            plt.close(fig)

            logger.info(f"Gauge chart saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to create gauge chart: {e}")
            plt.close('all')
            raise

    async def create_number_display(
        self,
        value: float,
        label: str,
        unit: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """
        Create a large number display visualization.

        Args:
            value: The numeric value to display
            label: Label for the value
            unit: Unit of measurement
            colors: List of color hex codes
            output_path: Path to save the chart

        Returns:
            Path to the saved chart
        """
        logger.info(f"Creating number display: {label}")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._create_number_display_sync,
            value, label, unit, colors, output_path
        )

    def _create_number_display_sync(
        self,
        value: float,
        label: str,
        unit: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """Synchronous number display creation."""
        try:
            if colors:
                self._style_manager.set_colors_from_hex(colors)

            style = self._style_manager.style
            primary_color = colors[0] if colors else self._style_manager.colors.primary

            fig, ax = plt.subplots(figsize=(6, 4))

            # Format value
            if value >= 1_000_000:
                value_text = f'{value / 1_000_000:.1f}M'
            elif value >= 1_000:
                value_text = f'{value / 1_000:.1f}K'
            else:
                value_text = f'{value:,.0f}'

            # Add unit
            if unit and unit not in ['items', 'units']:
                if unit == '%':
                    value_text = f'{value:.1f}%'
                elif unit in ['USD', 'EUR', 'GBP']:
                    value_text = f'${value:,.0f}' if unit == 'USD' else f'{unit} {value:,.0f}'

            # Draw value
            ax.text(
                0.5,
                0.55,
                value_text,
                ha='center',
                va='center',
                fontsize=48,
                fontweight='bold',
                color=primary_color,
                transform=ax.transAxes
            )

            # Draw label
            ax.text(
                0.5,
                0.25,
                label,
                ha='center',
                va='center',
                fontsize=16,
                color=self._style_manager.colors.text,
                transform=ax.transAxes
            )

            ax.axis('off')

            plt.tight_layout()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(
                output_path,
                dpi=style.figure_dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            plt.close(fig)

            logger.info(f"Number display saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to create number display: {e}")
            plt.close('all')
            raise

    def get_status(self) -> Dict[str, Any]:
        """Get engine status information."""
        return {
            "engine": "Matplotlib",
            "version": matplotlib.__version__,
            "backend": matplotlib.get_backend(),
            "is_active": self._is_active,
            "status": "ACTIVE" if self._is_active else "INACTIVE"
        }
