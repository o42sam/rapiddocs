from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.request import UploadResponse
from app.services.storage import storage_service
from app.config import settings

router = APIRouter()


@router.post("/upload/logo", response_model=UploadResponse)
async def upload_logo(file: UploadFile = File(...)):
    """Upload company logo"""
    # Validate file size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE} bytes"
        )

    # Validate file type
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in settings.allowed_formats_list:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {settings.ALLOWED_IMAGE_FORMATS}"
        )

    # Save file
    try:
        file_path = await storage_service.save_upload(content, file.filename, "logos")
        url = storage_service.get_public_url(file_path)

        return UploadResponse(
            filename=file.filename,
            url=file_path,  # Return full path for backend use
            size=len(content)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
