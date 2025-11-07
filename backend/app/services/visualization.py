import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
from typing import Tuple
from app.models.document import Statistic, DesignSpecification
from app.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import VisualizationError

logger = get_logger('visualization')


class VisualizationService:
    def __init__(self):
        self.dpi = settings.PDF_DPI

    def _hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB tuple (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    def _setup_plot_style(self, design_spec: DesignSpecification):
        """Apply color theme to plot"""
        color1 = self._hex_to_rgb(design_spec.foreground_color_1)
        color2 = self._hex_to_rgb(design_spec.foreground_color_2)

        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=[color1, color2])
        plt.rcParams['axes.facecolor'] = 'white'
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['font.size'] = 11
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14

    def _create_bar_chart(
        self,
        statistic: Statistic,
        design_spec: DesignSpecification
    ) -> bytes:
        """Create a bar chart"""
        fig, ax = plt.subplots(figsize=(8, 5), dpi=self.dpi)

        # Single bar chart
        color = self._hex_to_rgb(design_spec.foreground_color_1)
        ax.bar([statistic.name], [statistic.value], color=color, width=0.5)

        ax.set_ylabel(f"Value ({statistic.unit or ''})")
        ax.set_title(f"{statistic.name}", fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()

        # Save to bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=self.dpi)
        plt.close(fig)
        buffer.seek(0)
        return buffer.getvalue()

    def _create_pie_chart(
        self,
        statistic: Statistic,
        design_spec: DesignSpecification
    ) -> bytes:
        """Create a pie chart"""
        fig, ax = plt.subplots(figsize=(8, 5), dpi=self.dpi)

        # Create pie chart showing statistic value vs remainder
        if statistic.unit == '%':
            values = [statistic.value, 100 - statistic.value]
            labels = [statistic.name, 'Other']
        else:
            # For non-percentage values, just show the value
            values = [statistic.value, max(statistic.value * 0.2, 1)]
            labels = [statistic.name, 'Reference']

        colors = [
            self._hex_to_rgb(design_spec.foreground_color_1),
            self._hex_to_rgb(design_spec.foreground_color_2)
        ]

        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors,
               startangle=90, textprops={'fontsize': 11})
        ax.set_title(f"{statistic.name}", fontweight='bold', pad=20)

        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=self.dpi)
        plt.close(fig)
        buffer.seek(0)
        return buffer.getvalue()

    def _create_gauge_chart(
        self,
        statistic: Statistic,
        design_spec: DesignSpecification
    ) -> bytes:
        """Create a gauge chart"""
        fig, ax = plt.subplots(figsize=(8, 5), dpi=self.dpi, subplot_kw={'projection': 'polar'})

        # Determine max value for gauge
        if statistic.unit == '%':
            max_value = 100
        elif statistic.unit == '/5':
            max_value = 5
        else:
            max_value = statistic.value * 1.5

        # Calculate angle
        theta = (statistic.value / max_value) * 180 * (3.14159 / 180)

        # Create gauge
        ax.barh(1, theta, height=0.3, color=self._hex_to_rgb(design_spec.foreground_color_1))
        ax.set_ylim(0, 2)
        ax.set_xlim(0, 3.14159)
        ax.set_theta_zero_location('W')
        ax.set_theta_direction(1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['polar'].set_visible(False)

        # Add text
        ax.text(0, 1.7, f"{statistic.name}", ha='center', fontsize=14, fontweight='bold')
        ax.text(0, 0.3, f"{statistic.value}{statistic.unit or ''}", ha='center', fontsize=20)

        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=self.dpi)
        plt.close(fig)
        buffer.seek(0)
        return buffer.getvalue()

    def _create_line_chart(
        self,
        statistic: Statistic,
        design_spec: DesignSpecification
    ) -> bytes:
        """Create a line chart (showing trend)"""
        fig, ax = plt.subplots(figsize=(8, 5), dpi=self.dpi)

        # Simulate a trend line reaching the statistic value
        x = list(range(5))
        y = [statistic.value * 0.6, statistic.value * 0.7,
             statistic.value * 0.85, statistic.value * 0.95, statistic.value]

        color = self._hex_to_rgb(design_spec.foreground_color_1)
        ax.plot(x, y, marker='o', linewidth=2, color=color, markersize=8)
        ax.fill_between(x, y, alpha=0.3, color=color)

        ax.set_xlabel("Time Period")
        ax.set_ylabel(f"Value ({statistic.unit or ''})")
        ax.set_title(f"{statistic.name} Trend", fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xticks(x)
        ax.set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4', 'Current'])

        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=self.dpi)
        plt.close(fig)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_visualization(
        self,
        statistic: Statistic,
        design_spec: DesignSpecification
    ) -> bytes:
        """
        Generate visualization based on statistic type

        Args:
            statistic: Statistic data to visualize
            design_spec: Design specifications for styling

        Returns:
            Visualization image as bytes

        Raises:
            VisualizationError: If visualization generation fails
        """
        try:
            logger.info(f"Generating {statistic.visualization_type} visualization for '{statistic.name}'")

            self._setup_plot_style(design_spec)

            viz_type = statistic.visualization_type.lower()

            if viz_type == 'bar':
                result = self._create_bar_chart(statistic, design_spec)
            elif viz_type == 'pie':
                result = self._create_pie_chart(statistic, design_spec)
            elif viz_type == 'gauge':
                result = self._create_gauge_chart(statistic, design_spec)
            elif viz_type == 'line':
                result = self._create_line_chart(statistic, design_spec)
            else:
                logger.warning(f"Unknown visualization type '{viz_type}', defaulting to bar chart")
                result = self._create_bar_chart(statistic, design_spec)

            logger.info(f"Successfully generated visualization for '{statistic.name}'")
            return result

        except VisualizationError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate visualization for '{statistic.name}': {str(e)}", exc_info=True)
            raise VisualizationError(
                f"Failed to generate visualization: {str(e)}",
                details={
                    'statistic_name': statistic.name,
                    'visualization_type': statistic.visualization_type
                }
            )


visualization_service = VisualizationService()
