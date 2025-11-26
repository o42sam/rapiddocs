from datetime import datetime
from typing import List, Optional, Dict, Annotated
from pydantic import BaseModel, Field, BeforeValidator, PlainSerializer
from bson import ObjectId


def validate_object_id(v):
    """Validate and convert to ObjectId"""
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


# Pydantic v2 compatible ObjectId type
PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str)
]


class Statistic(BaseModel):
    name: str
    value: float
    unit: Optional[str] = None
    visualization_type: str = "bar"  # bar, line, pie, gauge


class DesignSpecification(BaseModel):
    background_color: str = "#FFFFFF"
    foreground_color_1: str = "#2563EB"
    foreground_color_2: str = "#06B6D4"
    theme_name: Optional[str] = "Ocean Blue"


class DocumentConfig(BaseModel):
    length: int  # Target word count
    document_type: str = "infographic"  # formal, infographic, or invoice
    use_watermark: bool = False  # Only applicable for formal documents with logo
    statistics: List[Statistic] = []
    design_spec: DesignSpecification


class DocumentFiles(BaseModel):
    logo_url: Optional[str] = None
    pdf_url: Optional[str] = None
    generated_images: List[str] = []
    visualizations: List[str] = []


class GenerationMetadata(BaseModel):
    text_model: str
    image_model: str
    word_count: int = 0
    generation_time_seconds: float = 0.0


class Document(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = "default"
    title: str
    description: str
    status: str = "pending"  # pending, processing, completed, failed
    config: DocumentConfig
    files: DocumentFiles = Field(default_factory=DocumentFiles)
    generation_metadata: Optional[GenerationMetadata] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class GenerationJob(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    document_id: PyObjectId
    user_id: str = "default"  # User who owns this job
    status: str = "pending"  # pending, processing, completed, failed
    progress: int = 0  # 0-100
    current_step: str = "initializing"
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
