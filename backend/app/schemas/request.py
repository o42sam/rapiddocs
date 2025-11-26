from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class StatisticRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: float
    unit: Optional[str] = Field(None, max_length=20)
    visualization_type: str = Field("bar", pattern="^(bar|line|pie|gauge)$")


class DesignSpecRequest(BaseModel):
    background_color: str = Field("#FFFFFF", pattern="^#[0-9A-Fa-f]{6}$")
    foreground_color_1: str = Field(..., pattern="^#[0-9A-Fa-f]{6}$")
    foreground_color_2: str = Field(..., pattern="^#[0-9A-Fa-f]{6}$")
    theme_name: Optional[str] = Field(None, max_length=50)


class DocumentGenerationRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=2000)
    length: int = Field(..., ge=500, le=10000)
    document_type: str = Field("infographic", pattern="^(formal|infographic|invoice)$")
    use_watermark: bool = Field(False)  # Only applicable for formal documents with logo
    statistics: List[StatisticRequest] = Field(default_factory=list, max_length=10)
    design_spec: DesignSpecRequest

    @field_validator('statistics')
    @classmethod
    def validate_statistics(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 statistics allowed')
        return v

    @field_validator('document_type')
    @classmethod
    def validate_document_type(cls, v):
        if v not in ['formal', 'infographic', 'invoice']:
            raise ValueError('document_type must be "formal", "infographic", or "invoice"')
        return v


class DocumentResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    pdf_url: Optional[str] = None


class GenerationJobResponse(BaseModel):
    job_id: str
    status: str
    message: str = "Document generation started"
    estimated_time_seconds: int = 120


class JobStatusResponse(BaseModel):
    job_id: str
    document_id: Optional[str] = None
    status: str
    progress: int
    current_step: str
    error_message: Optional[str] = None


class UploadResponse(BaseModel):
    filename: str
    url: str
    size: int
