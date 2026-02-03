"""
Infographic Document Routes.
API endpoints for infographic document generation.
"""

import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse

from ..schemas.infographic_schemas import (
    InfographicGenerateRequest,
    InfographicGenerateResponse,
    InfographicStatusResponse,
    ImportDataRequest,
    ImportDataResponse,
    ComponentStatusResponse,
    StatisticSchema
)
from ...application.dto.infographic_request import InfographicRequest, StatisticDTO
from ...application.use_cases.generate_infographic import GenerateInfographicUseCase
from ...infrastructure.ai_providers.gemini_text_generator import GeminiTextGenerator
from ...infrastructure.ai_providers.banana_image_generator import BananaImageGenerator
from ...infrastructure.ai_providers.prompt_analyzer import PromptAnalyzer
from ...infrastructure.visualization.matplotlib_engine import MatplotlibEngine
from ...infrastructure.document_renderers.infographic_pdf_renderer import InfographicPDFRenderer
from ...infrastructure.data_import.csv_importer import CSVImporter
from ...infrastructure.data_import.excel_importer import ExcelImporter
from ...config import settings
from ...shared.logger import get_logger

logger = get_logger("infographic_routes")

router = APIRouter(prefix="/infographic", tags=["Infographic Documents"])

# In-memory job storage (replace with database in production)
_job_storage = {}


def get_text_generator() -> GeminiTextGenerator:
    """Dependency for text generator."""
    return GeminiTextGenerator(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL
    )


def get_image_generator() -> BananaImageGenerator:
    """Dependency for image generator."""
    return BananaImageGenerator(
        api_key=settings.HUGGINGFACE_API_KEY,
        model=settings.IMAGE_GENERATION_MODEL
    )


def get_visualization_engine() -> MatplotlibEngine:
    """Dependency for visualization engine."""
    return MatplotlibEngine()


def get_document_renderer() -> InfographicPDFRenderer:
    """Dependency for document renderer."""
    return InfographicPDFRenderer()


def get_prompt_analyzer(
    text_generator: GeminiTextGenerator = Depends(get_text_generator)
) -> PromptAnalyzer:
    """Dependency for prompt analyzer."""
    return PromptAnalyzer(text_generator)


def get_csv_importer() -> CSVImporter:
    """Dependency for CSV importer."""
    return CSVImporter()


def get_excel_importer() -> ExcelImporter:
    """Dependency for Excel importer."""
    return ExcelImporter()


def get_infographic_use_case(
    text_generator: GeminiTextGenerator = Depends(get_text_generator),
    image_generator: BananaImageGenerator = Depends(get_image_generator),
    visualization_engine: MatplotlibEngine = Depends(get_visualization_engine),
    document_renderer: InfographicPDFRenderer = Depends(get_document_renderer),
    prompt_analyzer: PromptAnalyzer = Depends(get_prompt_analyzer),
    csv_importer: CSVImporter = Depends(get_csv_importer)
) -> GenerateInfographicUseCase:
    """Dependency for the infographic generation use case."""
    return GenerateInfographicUseCase(
        text_generator=text_generator,
        image_generator=image_generator,
        visualization_engine=visualization_engine,
        document_renderer=document_renderer,
        prompt_analyzer=prompt_analyzer,
        data_importer=csv_importer
    )


@router.post(
    "/generate",
    response_model=InfographicGenerateResponse,
    summary="Generate Infographic Document",
    description="Generate a professional infographic document with AI-generated text, "
                "charts, and illustrations based on the provided topic/prompt."
)
async def generate_infographic(
    request: InfographicGenerateRequest,
    background_tasks: BackgroundTasks,
    use_case: GenerateInfographicUseCase = Depends(get_infographic_use_case)
) -> InfographicGenerateResponse:
    """
    Generate an infographic document.

    The topic/prompt is analyzed by AI to extract:
    - Document title
    - Target word count
    - Statistics and their visualization types
    - Section structure

    Text content is generated with proper enumeration (no bullet points),
    charts are created for each statistic, and illustrations are generated
    for each section.
    """
    job_id = str(uuid.uuid4())[:8]
    logger.info(f"Infographic generation request received - Job ID: {job_id}")

    try:
        # Convert schema to DTO
        statistics = []
        if request.statistics:
            statistics = [
                StatisticDTO(
                    name=s.name,
                    value=s.value,
                    unit=s.unit,
                    visualization_type=s.visualization_type,
                    category=s.category,
                    description=s.description
                )
                for s in request.statistics
            ]

        dto = InfographicRequest(
            title=request.title or "",
            topic=request.topic,
            statistics=statistics,
            num_sections=request.num_sections,
            num_images=request.num_images,
            color_scheme=request.color_scheme,
            logo_path=request.logo_path,
            output_format=request.output_format,
            include_cover_page=request.include_cover_page
        )

        # Validate request
        validation_errors = dto.validate()
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail={"errors": validation_errors}
            )

        # Store job status
        _job_storage[job_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting generation..."
        }

        # Execute generation (could be moved to background for long tasks)
        output_path = await use_case.execute(dto)

        # Update job status
        _job_storage[job_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Generation complete",
            "file_path": str(output_path)
        }

        # Build download URL
        download_url = f"{settings.API_PREFIX}/infographic/download/{job_id}"

        return InfographicGenerateResponse(
            success=True,
            job_id=job_id,
            message="Infographic document generated successfully",
            file_path=str(output_path),
            download_url=download_url,
            metadata={
                "sections": dto.num_sections,
                "images": dto.num_images,
                "format": dto.output_format
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Infographic generation failed: {e}")
        _job_storage[job_id] = {
            "status": "failed",
            "progress": 0,
            "message": str(e),
            "error": str(e)
        }
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate infographic: {str(e)}"
        )


@router.get(
    "/status/{job_id}",
    response_model=InfographicStatusResponse,
    summary="Check Generation Status",
    description="Check the status of an infographic generation job."
)
async def get_job_status(job_id: str) -> InfographicStatusResponse:
    """Get the status of a generation job."""
    if job_id not in _job_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {job_id}"
        )

    job = _job_storage[job_id]
    return InfographicStatusResponse(
        job_id=job_id,
        status=job.get("status", "unknown"),
        progress=job.get("progress", 0),
        message=job.get("message"),
        file_path=job.get("file_path"),
        error=job.get("error")
    )


@router.get(
    "/download/{job_id}",
    summary="Download Generated Document",
    description="Download the generated infographic document."
)
async def download_infographic(job_id: str) -> FileResponse:
    """Download the generated infographic document."""
    if job_id not in _job_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {job_id}"
        )

    job = _job_storage[job_id]

    if job.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Status: {job.get('status')}"
        )

    file_path = job.get("file_path")
    if not file_path or not Path(file_path).exists():
        raise HTTPException(
            status_code=404,
            detail="Generated file not found"
        )

    filename = Path(file_path).name
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )


@router.post(
    "/import-data",
    response_model=ImportDataResponse,
    summary="Import Statistics Data",
    description="Import statistics from a CSV or Excel file."
)
async def import_statistics_data(
    request: ImportDataRequest,
    csv_importer: CSVImporter = Depends(get_csv_importer),
    excel_importer: ExcelImporter = Depends(get_excel_importer)
) -> ImportDataResponse:
    """
    Import statistics data from a file.

    Expected columns:
    - name: Statistic name
    - value: Numeric value
    - unit: Unit of measurement
    - visualization_type: Chart type (bar_chart, line_chart, pie_chart, gauge_chart, number)
    - category: Optional category
    - description: Optional description
    """
    file_path = Path(request.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {request.file_path}"
        )

    try:
        # Choose importer based on file type
        if request.file_type.lower() == 'excel' or file_path.suffix.lower() in ['.xlsx', '.xls']:
            importer = excel_importer
        else:
            importer = csv_importer

        # Import data
        data = await importer.import_file(file_path)

        # Convert to schema
        statistics = [
            StatisticSchema(
                name=item.get('name', 'Unnamed'),
                value=float(item.get('value', 0)),
                unit=item.get('unit', 'units'),
                visualization_type=item.get('visualization_type', 'bar_chart'),
                category=item.get('category'),
                description=item.get('description')
            )
            for item in data
        ]

        # Get preview
        preview = importer.preview(file_path, rows=5)

        return ImportDataResponse(
            success=True,
            message=f"Successfully imported {len(data)} statistics",
            statistics=statistics,
            row_count=len(data),
            preview=preview
        )

    except Exception as e:
        logger.error(f"Data import failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import data: {str(e)}"
        )


@router.get(
    "/status",
    response_model=ComponentStatusResponse,
    summary="Get Component Status",
    description="Get the status of all infographic generation components."
)
async def get_component_status(
    text_generator: GeminiTextGenerator = Depends(get_text_generator),
    image_generator: BananaImageGenerator = Depends(get_image_generator),
    visualization_engine: MatplotlibEngine = Depends(get_visualization_engine),
    document_renderer: InfographicPDFRenderer = Depends(get_document_renderer)
) -> ComponentStatusResponse:
    """Get status of all generation components."""
    return ComponentStatusResponse(
        text_generator=text_generator.get_status_info() if hasattr(text_generator, 'get_status_info') else {
            "provider": text_generator.provider_name,
            "model": text_generator.model_name,
            "is_active": getattr(text_generator, 'is_active', True)
        },
        image_generator=image_generator.get_status() if hasattr(image_generator, 'get_status') else {
            "model": image_generator.model_name,
            "is_active": getattr(image_generator, 'is_active', True)
        },
        visualization_engine=visualization_engine.get_status() if hasattr(visualization_engine, 'get_status') else {
            "engine": "Matplotlib",
            "is_active": True
        },
        document_renderer=document_renderer.get_status() if hasattr(document_renderer, 'get_status') else {
            "renderer": "InfographicPDFRenderer",
            "is_active": True
        }
    )
