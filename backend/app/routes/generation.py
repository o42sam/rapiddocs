from fastapi import APIRouter, HTTPException, BackgroundTasks, Form, UploadFile, File, Depends
from fastapi.responses import FileResponse
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
import asyncio
import time
import json
import os

from app.database import get_database
from app.models.user import User
from app.utils.dependencies import get_current_active_user
from app.schemas.request import (
    DocumentGenerationRequest,
    GenerationJobResponse,
    JobStatusResponse,
    StatisticRequest,
    DesignSpecRequest
)
from app.models.document import (
    Document,
    GenerationJob,
    DocumentConfig,
    DesignSpecification,
    Statistic,
    DocumentFiles,
    GenerationMetadata
)
from app.services.text_generation import text_generation_service
from app.services.image_generation import image_generation_service
from app.services.visualization import visualization_service
from app.services.pdf_generator import pdf_generator_service
from app.services.watermark import watermark_service
from app.services.storage import storage_service
from app.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import (
    DocumentGenerationError,
    TextGenerationError,
    ImageGenerationError,
    VisualizationError,
    PDFGenerationError
)

logger = get_logger('generation_route')
router = APIRouter()


async def generate_document_task(job_id: str, doc_id: str, logo_path: Optional[str]):
    """
    Background task to generate document

    This task handles both formal and infographic document types:
    - Formal: Text only, no images or visualizations
    - Infographic: Text + AI-generated images + data visualizations
    """
    db = get_database()
    start_time = time.time()

    try:
        logger.info(f"Starting document generation task: job_id={job_id}, doc_id={doc_id}")

        # Get document
        doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
        if not doc:
            logger.error(f"Document not found: doc_id={doc_id}")
            raise DocumentGenerationError("Document not found", details={'doc_id': doc_id})

        # Extract document type and watermark preference
        document_type = doc["config"].get("document_type", "infographic")
        use_watermark = doc["config"].get("use_watermark", False)
        logger.info(f"Document type: {document_type}, use_watermark: {use_watermark}")

        # Update job status
        await db.generation_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "status": "processing",
                    "progress": 10,
                    "current_step": "generating_text",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Convert statistics to model
        statistics = [
            Statistic(**stat) for stat in doc["config"]["statistics"]
        ]
        logger.info(f"Processing {len(statistics)} statistics")

        # Generate text (run in thread pool since it's blocking)
        logger.info("Starting text generation")
        generated_text = await asyncio.to_thread(
            text_generation_service.generate_text,
            description=doc["description"],
            word_count=doc["config"]["length"],
            statistics=statistics
        )

        # Extract title
        title = text_generation_service.extract_title(generated_text)
        logger.info(f"Extracted title: {title}")

        # Update document with title
        await db.documents.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {"title": title, "updated_at": datetime.utcnow()}}
        )

        # Update progress
        await db.generation_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "progress": 30,
                    "current_step": "generating_images" if document_type == "infographic" else "assembling_pdf",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Initialize paths for images and visualizations
        design_spec = DesignSpecification(**doc["config"]["design_spec"])
        image_paths = []
        viz_paths = []

        # Generate images and visualizations ONLY for infographic type
        if document_type == "infographic":
            logger.info("Generating images for infographic document")

            # Generate images (2 images)
            try:
                images = image_generation_service.generate_multiple_images(
                    document_theme=doc["description"][:100],
                    color1=design_spec.foreground_color_1,
                    color2=design_spec.foreground_color_2,
                    count=2
                )

                for i, img_data in enumerate(images):
                    img_path = await storage_service.save_generated_image(img_data, doc_id, i + 1)
                    image_paths.append(img_path)

                logger.info(f"Successfully generated {len(image_paths)} images")
            except ImageGenerationError as e:
                logger.error(f"Image generation failed: {e.message}")
                # Continue without images for infographic type
            except Exception as e:
                logger.error(f"Unexpected error in image generation: {str(e)}")
                # Continue without images

            # Update progress
            await db.generation_jobs.update_one(
                {"_id": ObjectId(job_id)},
                {
                    "$set": {
                        "progress": 50,
                        "current_step": "generating_visualizations",
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            # Generate visualizations
            logger.info("Generating data visualizations for infographic document")
            for stat in statistics:
                try:
                    viz_data = visualization_service.generate_visualization(stat, design_spec)
                    viz_path = await storage_service.save_visualization(viz_data, doc_id, stat.name)
                    viz_paths.append(viz_path)
                except VisualizationError as e:
                    logger.error(f"Visualization failed for {stat.name}: {e.message}")
                except Exception as e:
                    logger.error(f"Unexpected error visualizing {stat.name}: {str(e)}")

            logger.info(f"Successfully generated {len(viz_paths)} visualizations")

        elif document_type == "formal":
            logger.info("Skipping images and visualizations for formal document")

        # Update progress
        await db.generation_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "progress": 70,
                    "current_step": "assembling_pdf",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Generate PDF with document_type parameter
        logger.info("Starting PDF assembly")
        pdf_path = storage_service.get_pdf_path(doc_id, title)

        try:
            pdf_generator_service.generate_pdf(
                output_path=pdf_path,
                title=title,
                content=generated_text,
                design_spec=design_spec,
                document_type=document_type,
                use_watermark=False,  # Don't use ReportLab watermark anymore
                logo_path=logo_path,
                image_paths=image_paths,
                visualization_paths=viz_paths
            )
            logger.info(f"PDF generated successfully: {pdf_path}")

            # Apply watermark as post-processing step if requested
            if use_watermark and document_type == "formal" and logo_path and os.path.exists(logo_path):
                logger.info("Applying watermark to PDF using PyPDF2")

                # Create temporary path for watermarked PDF
                watermarked_path = pdf_path.replace('.pdf', '_watermarked.pdf')

                # Apply watermark
                await asyncio.to_thread(
                    watermark_service.add_watermark_to_pdf,
                    input_pdf_path=pdf_path,
                    output_pdf_path=watermarked_path,
                    logo_path=logo_path,
                    skip_first_page=True,
                    opacity=0.15
                )

                # Replace original PDF with watermarked version
                os.replace(watermarked_path, pdf_path)
                logger.info(f"Watermark applied successfully to: {pdf_path}")

        except PDFGenerationError as e:
            logger.error(f"PDF generation failed: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in PDF generation: {str(e)}")
            raise PDFGenerationError(f"PDF generation failed: {str(e)}")

        # Calculate generation time
        generation_time = time.time() - start_time
        logger.info(f"Total generation time: {generation_time:.2f} seconds")

        # Update document
        pdf_url = storage_service.get_public_url(pdf_path)
        await db.documents.update_one(
            {"_id": ObjectId(doc_id)},
            {
                "$set": {
                    "status": "completed",
                    "files": {
                        "logo_url": logo_path,
                        "pdf_url": pdf_url,
                        "generated_images": image_paths,
                        "visualizations": viz_paths
                    },
                    "generation_metadata": {
                        "text_model": settings.TEXT_GENERATION_MODEL,
                        "image_model": settings.IMAGE_GENERATION_MODEL,
                        "word_count": len(generated_text.split()),
                        "generation_time_seconds": generation_time
                    },
                    "updated_at": datetime.utcnow(),
                    "completed_at": datetime.utcnow()
                }
            }
        )

        # Update job
        await db.generation_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "status": "completed",
                    "progress": 100,
                    "current_step": "completed",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        logger.info(f"Document generation completed successfully: doc_id={doc_id}")

    except (TextGenerationError, ImageGenerationError, VisualizationError, PDFGenerationError, DocumentGenerationError) as e:
        # Handle known exceptions
        logger.error(f"Document generation failed with known error: {e.message}", exc_info=True)
        error_msg = f"{e.__class__.__name__}: {e.message}"

        # Update job with error
        await db.generation_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "status": "failed",
                    "error_message": error_msg,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Update document
        await db.documents.update_one(
            {"_id": ObjectId(doc_id)},
            {
                "$set": {
                    "status": "failed",
                    "error_message": error_msg,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    except Exception as e:
        # Handle unexpected exceptions
        logger.error(f"Document generation failed with unexpected error: {str(e)}", exc_info=True)

        # Update job with error
        await db.generation_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "status": "failed",
                    "error_message": str(e),
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Update document
        await db.documents.update_one(
            {"_id": ObjectId(doc_id)},
            {
                "$set": {
                    "status": "failed",
                    "error_message": str(e),
                    "updated_at": datetime.utcnow()
                }
            }
        )


@router.post("/generate/document", response_model=GenerationJobResponse)
async def generate_document(
    background_tasks: BackgroundTasks,
    description: str = Form(...),
    length: int = Form(...),
    document_type: str = Form("infographic"),  # formal or infographic
    use_watermark: bool = Form(False),  # Whether to use logo as watermark (formal only)
    statistics: str = Form(...),  # JSON string
    design_spec: str = Form(...),  # JSON string
    logo: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a new document

    Args:
        description: Document description/theme
        length: Target word count (500-5000)
        document_type: Type of document - "formal" (text only) or "infographic" (text + images + charts)
        use_watermark: Whether to use logo as watermark (only applicable for formal documents with logo)
        statistics: JSON string of statistics array
        design_spec: JSON string of design specifications
        logo: Optional company logo file

    Returns:
        Generation job response with job_id and status
    """
    logger.info(f"Received document generation request: type={document_type}, length={length}")

    db = get_database()

    # Validate document_type
    if document_type not in ['formal', 'infographic']:
        logger.warning(f"Invalid document_type received: {document_type}")
        raise HTTPException(
            status_code=400,
            detail="document_type must be either 'formal' or 'infographic'"
        )

    # Parse JSON fields
    try:
        stats_data = json.loads(statistics)
        design_data = json.loads(design_spec)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON in request")

    # Validate
    if length < 500 or length > 10000:
        logger.warning(f"Invalid length: {length}")
        raise HTTPException(status_code=400, detail="Length must be between 500 and 10,000 words")

    # Handle logo upload
    logo_path = None
    if logo:
        logger.info(f"Processing logo upload: {logo.filename}")
        content = await logo.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            logger.warning(f"Logo file too large: {len(content)} bytes")
            raise HTTPException(status_code=400, detail="Logo file too large")

        logo_path = await storage_service.save_upload(content, logo.filename, "logos")
        logger.info(f"Logo saved: {logo_path}")

    # Create document config
    doc_config = DocumentConfig(
        length=length,
        document_type=document_type,
        use_watermark=use_watermark,
        statistics=[Statistic(**s) for s in stats_data],
        design_spec=DesignSpecification(**design_data)
    )
    logger.info(f"Created document config with {len(stats_data)} statistics, watermark={use_watermark}")

    # Create document with user_id
    document = Document(
        user_id=str(current_user.id),
        description=description,
        title="Generating...",
        status="pending",
        config=doc_config
    )

    # Insert to database
    result = await db.documents.insert_one(document.dict(by_alias=True, exclude={"id"}))
    doc_id = str(result.inserted_id)

    # Create generation job
    job = GenerationJob(
        document_id=ObjectId(doc_id),
        status="pending",
        progress=0,
        current_step="initializing"
    )

    job_result = await db.generation_jobs.insert_one(job.dict(by_alias=True, exclude={"id"}))
    job_id = str(job_result.inserted_id)

    # Start background task
    background_tasks.add_task(generate_document_task, job_id, doc_id, logo_path)

    logger.info(f"Document generation task started: job_id={job_id}, doc_id={doc_id}, type={document_type}")

    return GenerationJobResponse(
        job_id=job_id,
        status="processing",
        message=f"Document generation started ({document_type} type)",
        estimated_time_seconds=120 if document_type == "infographic" else 60
    )


@router.get("/generate/status/{job_id}", response_model=JobStatusResponse)
async def get_generation_status(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get generation job status (only for user's own jobs)"""
    db = get_database()

    try:
        job = await db.generation_jobs.find_one({"_id": ObjectId(job_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify the job belongs to the current user
    doc = await db.documents.find_one({"_id": job["document_id"]})
    if not doc or doc.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job_id,
        document_id=str(job["document_id"]),
        status=job["status"],
        progress=job["progress"],
        current_step=job["current_step"],
        error_message=job.get("error_message")
    )


@router.get("/generate/download/{job_id}")
async def download_document(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Download generated PDF (only for user's own documents)"""
    db = get_database()

    try:
        job = await db.generation_jobs.find_one({"_id": ObjectId(job_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Document generation not completed")

    # Get document - convert document_id string to ObjectId
    doc_id = job["document_id"]
    if isinstance(doc_id, str):
        doc_id = ObjectId(doc_id)

    doc = await db.documents.find_one({
        "_id": doc_id,
        "user_id": str(current_user.id)
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    pdf_url = doc.get("files", {}).get("pdf_url")
    if not pdf_url:
        raise HTTPException(status_code=404, detail="PDF not found")

    # Get actual file path - extract filename from URL
    filename = os.path.basename(pdf_url)
    pdf_path = os.path.join(settings.PDF_OUTPUT_DIR, filename)

    if not storage_service.file_exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{doc['title']}.pdf"
    )
