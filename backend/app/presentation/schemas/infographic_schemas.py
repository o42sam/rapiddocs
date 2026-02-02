"""
Infographic API Schemas.
Pydantic models for infographic document generation API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class StatisticSchema(BaseModel):
    """Schema for a statistic in the infographic."""
    name: str = Field(..., min_length=1, max_length=100, description="Statistic name")
    value: float = Field(..., description="Numeric value")
    unit: str = Field(default="units", max_length=20, description="Unit of measurement")
    visualization_type: str = Field(
        default="bar_chart",
        description="Chart type: bar_chart, line_chart, pie_chart, gauge_chart, number"
    )
    category: Optional[str] = Field(None, max_length=50, description="Optional category")
    description: Optional[str] = Field(None, max_length=200, description="Optional description")

    @field_validator('visualization_type')
    @classmethod
    def validate_visualization_type(cls, v: str) -> str:
        valid_types = ['bar_chart', 'line_chart', 'pie_chart', 'gauge_chart', 'number']
        if v.lower() not in valid_types:
            raise ValueError(f"visualization_type must be one of: {', '.join(valid_types)}")
        return v.lower()


class InfographicGenerateRequest(BaseModel):
    """Request schema for infographic generation."""
    topic: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Topic/prompt describing what the infographic should cover. "
                    "Can include desired word count (e.g., '500 words'), statistics, "
                    "and any specific requirements."
    )
    title: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional explicit title (will be extracted from topic if not provided)"
    )
    statistics: Optional[List[StatisticSchema]] = Field(
        default=None,
        description="Optional list of statistics to include. If not provided, "
                    "will be extracted from the topic."
    )
    num_sections: int = Field(
        default=3,
        ge=2,
        le=8,
        description="Number of sections in the document"
    )
    num_images: int = Field(
        default=3,
        ge=2,
        le=4,
        description="Number of illustrations to generate (2-4)"
    )
    color_scheme: Optional[List[str]] = Field(
        default=None,
        description="List of hex color codes for the document theme"
    )
    logo_path: Optional[str] = Field(
        None,
        description="Path to logo file (must be previously uploaded)"
    )
    output_format: str = Field(
        default="pdf",
        description="Output format (currently only 'pdf' is supported)"
    )
    include_cover_page: bool = Field(
        default=True,
        description="Whether to include a cover page"
    )

    @field_validator('color_scheme')
    @classmethod
    def validate_colors(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return None
        for color in v:
            if not color.startswith('#') or len(color) != 7:
                raise ValueError(f"Invalid color format: {color}. Use hex format like #1e40af")
        return v

    @field_validator('output_format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        valid_formats = ['pdf']  # Can add more later: 'docx', 'html'
        if v.lower() not in valid_formats:
            raise ValueError(f"output_format must be one of: {', '.join(valid_formats)}")
        return v.lower()


class InfographicGenerateResponse(BaseModel):
    """Response schema for infographic generation."""
    success: bool = Field(..., description="Whether generation was successful")
    job_id: str = Field(..., description="Unique job identifier")
    message: str = Field(..., description="Status message")
    file_path: Optional[str] = Field(None, description="Path to generated file")
    download_url: Optional[str] = Field(None, description="URL to download the document")
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class InfographicStatusResponse(BaseModel):
    """Response schema for job status check."""
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status: pending, processing, completed, failed")
    progress: float = Field(default=0.0, ge=0, le=100, description="Progress percentage")
    message: Optional[str] = Field(None, description="Status message")
    file_path: Optional[str] = Field(None, description="Path to generated file if completed")
    error: Optional[str] = Field(None, description="Error message if failed")


class ImportDataRequest(BaseModel):
    """Request schema for data import."""
    file_path: str = Field(..., description="Path to uploaded CSV/Excel file")
    file_type: str = Field(default="csv", description="File type: csv or excel")


class ImportDataResponse(BaseModel):
    """Response schema for data import."""
    success: bool = Field(..., description="Whether import was successful")
    message: str = Field(..., description="Status message")
    statistics: Optional[List[StatisticSchema]] = Field(
        None,
        description="Imported statistics"
    )
    row_count: int = Field(default=0, description="Number of rows imported")
    preview: Optional[List[dict]] = Field(None, description="Preview of first few rows")


class ComponentStatusResponse(BaseModel):
    """Response schema for component status."""
    text_generator: dict = Field(..., description="Text generator status")
    image_generator: dict = Field(..., description="Image generator status")
    visualization_engine: dict = Field(..., description="Visualization engine status")
    document_renderer: dict = Field(..., description="Document renderer status")
