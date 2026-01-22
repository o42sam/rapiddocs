"""
Statistic Value Object.
Represents statistical data for infographic documents.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class VisualizationType(Enum):
    """Types of visualizations for statistics."""
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    GAUGE_CHART = "gauge_chart"
    TABLE = "table"
    NUMBER = "number"


@dataclass(frozen=True)
class Statistic:
    """
    Immutable value object representing a statistic.

    Attributes:
        name: Name or label of the statistic
        value: Numeric value of the statistic
        unit: Unit of measurement (e.g., %, USD, items)
        visualization_type: How this statistic should be visualized
        category: Optional category for grouping
        description: Optional description of the statistic
    """
    name: str
    value: float
    unit: str
    visualization_type: VisualizationType
    category: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self):
        """Validate statistic data."""
        if not self.name:
            raise ValueError("Statistic name is required")
        if not self.unit:
            raise ValueError("Unit is required")

    @property
    def formatted_value(self) -> str:
        """Get formatted value with unit."""
        if self.unit == "%":
            return f"{self.value:.1f}{self.unit}"
        elif self.unit in ["USD", "EUR", "GBP"]:
            return f"{self.unit} {self.value:,.2f}"
        else:
            return f"{self.value:,.0f} {self.unit}"

    @classmethod
    def percentage(
        cls,
        name: str,
        value: float,
        visualization: VisualizationType = VisualizationType.GAUGE_CHART
    ) -> "Statistic":
        """Create a percentage statistic."""
        return cls(
            name=name,
            value=value,
            unit="%",
            visualization_type=visualization
        )

    @classmethod
    def currency(
        cls,
        name: str,
        value: float,
        currency: str = "USD",
        visualization: VisualizationType = VisualizationType.BAR_CHART
    ) -> "Statistic":
        """Create a currency statistic."""
        return cls(
            name=name,
            value=value,
            unit=currency,
            visualization_type=visualization
        )

    @classmethod
    def count(
        cls,
        name: str,
        value: float,
        unit: str = "items",
        visualization: VisualizationType = VisualizationType.NUMBER
    ) -> "Statistic":
        """Create a count statistic."""
        return cls(
            name=name,
            value=value,
            unit=unit,
            visualization_type=visualization
        )

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "visualization_type": self.visualization_type.value,
            "category": self.category,
            "description": self.description,
            "formatted_value": self.formatted_value
        }