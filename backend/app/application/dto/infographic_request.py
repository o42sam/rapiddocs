"""
Infographic Request DTO.
Data transfer object for infographic document generation requests.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class StatisticDTO:
    """DTO for statistics in infographic."""
    name: str
    value: float
    unit: str
    visualization_type: str  # bar_chart, line_chart, pie_chart, gauge_chart, number
    category: Optional[str] = None
    description: Optional[str] = None


@dataclass
class InfographicRequest:
    """
    DTO for infographic generation request.

    Attributes:
        title: Document title
        topic: Main topic for content generation
        statistics: List of statistics to visualize
        num_sections: Number of text sections to generate
        num_images: Number of AI-generated images (2-4)
        color_scheme: List of hex color codes
        logo_path: Optional path to logo file
        output_format: Output format (pdf, docx, html, md)
        import_file_path: Optional path to CSV/Excel file for statistics
        include_cover_page: Whether to include a cover page
        user_id: ID of requesting user
    """
    title: str
    topic: str
    statistics: List[StatisticDTO]
    num_sections: int = 3
    num_images: int = 3
    color_scheme: List[str] = None
    logo_path: Optional[str] = None
    output_format: str = "pdf"
    import_file_path: Optional[str] = None
    include_cover_page: bool = True
    user_id: Optional[str] = None

    def __post_init__(self):
        """Set defaults and validate."""
        if self.color_scheme is None:
            self.color_scheme = ["#1e40af", "#3730a3", "#7c3aed"]

        # Ensure num_images is between 2 and 4
        self.num_images = max(2, min(4, self.num_images))

    def validate(self) -> List[str]:
        """
        Validate the request.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.title:
            errors.append("Title is required")
        if not self.topic:
            errors.append("Topic is required")
        if not self.statistics and not self.import_file_path:
            errors.append("Statistics or import file path is required")

        valid_visualizations = ["bar_chart", "line_chart", "pie_chart", "gauge_chart", "number"]
        for stat in self.statistics:
            if not stat.name:
                errors.append("Statistic name is required")
            if stat.visualization_type not in valid_visualizations:
                errors.append(
                    f"Invalid visualization type for {stat.name}. "
                    f"Must be one of: {', '.join(valid_visualizations)}"
                )

        if self.num_sections < 1:
            errors.append("Number of sections must be at least 1")
        if not 2 <= self.num_images <= 4:
            errors.append("Number of images must be between 2 and 4")

        valid_formats = ["pdf", "docx", "html", "md"]
        if self.output_format not in valid_formats:
            errors.append(f"Invalid output format. Must be one of: {', '.join(valid_formats)}")

        for color in self.color_scheme:
            if not color.startswith("#") or len(color) != 7:
                errors.append(f"Invalid color code: {color}")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "topic": self.topic,
            "statistics": [
                {
                    "name": stat.name,
                    "value": stat.value,
                    "unit": stat.unit,
                    "visualization_type": stat.visualization_type,
                    "category": stat.category,
                    "description": stat.description
                }
                for stat in self.statistics
            ],
            "num_sections": self.num_sections,
            "num_images": self.num_images,
            "color_scheme": self.color_scheme,
            "logo_path": self.logo_path,
            "output_format": self.output_format,
            "import_file_path": self.import_file_path,
            "include_cover_page": self.include_cover_page,
            "user_id": self.user_id
        }