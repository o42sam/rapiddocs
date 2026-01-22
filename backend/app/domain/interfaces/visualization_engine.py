"""
Visualization Engine Interface.
Defines the contract for chart and graph generation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path


class IVisualizationEngine(ABC):
    """
    Interface for chart/graph generation.
    Implementations: Matplotlib, Plotly, Chart.js backend
    """

    @abstractmethod
    async def create_bar_chart(
        self,
        data: Dict[str, float],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """
        Create bar chart.

        Args:
            data: Dictionary of labels to values
            title: Chart title
            colors: List of color hex codes
            output_path: Path to save the chart

        Returns:
            Path to the saved chart
        """
        pass

    @abstractmethod
    async def create_line_chart(
        self,
        data: Dict[str, List[float]],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """
        Create line chart.

        Args:
            data: Dictionary of series names to value lists
            title: Chart title
            colors: List of color hex codes
            output_path: Path to save the chart

        Returns:
            Path to the saved chart
        """
        pass

    @abstractmethod
    async def create_pie_chart(
        self,
        data: Dict[str, float],
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """
        Create pie chart.

        Args:
            data: Dictionary of labels to values
            title: Chart title
            colors: List of color hex codes
            output_path: Path to save the chart

        Returns:
            Path to the saved chart
        """
        pass

    @abstractmethod
    async def create_gauge_chart(
        self,
        value: float,
        max_value: float,
        title: str,
        colors: List[str],
        output_path: Path
    ) -> Path:
        """
        Create gauge chart.

        Args:
            value: Current value
            max_value: Maximum value for scale
            title: Chart title
            colors: List of color hex codes
            output_path: Path to save the chart

        Returns:
            Path to the saved chart
        """
        pass