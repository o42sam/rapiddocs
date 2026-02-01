"""
GridFS Storage Service for MongoDB file storage.
Stores logos, PDFs, and other files in MongoDB instead of local filesystem.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from io import BytesIO
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class GridFSStorage:
    """Service for storing and retrieving files from MongoDB GridFS."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize GridFS storage.

        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.fs = AsyncIOMotorGridFSBucket(db)
        # Separate buckets for different file types
        self.logos_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="logos")
        self.pdfs_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="pdfs")

    async def store_logo(
        self,
        file_data: bytes,
        filename: str,
        job_id: str,
        content_type: str = "image/png",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a logo file in GridFS.

        Args:
            file_data: Binary content of the logo
            filename: Original filename
            job_id: Associated job ID
            content_type: MIME type of the file
            metadata: Additional metadata

        Returns:
            GridFS file ID as string
        """
        try:
            file_metadata = {
                "job_id": job_id,
                "content_type": content_type,
                "original_filename": filename,
                "uploaded_at": datetime.utcnow(),
                **(metadata or {})
            }

            grid_in = self.logos_bucket.open_upload_stream(
                filename=f"{job_id}_{filename}",
                metadata=file_metadata
            )

            await grid_in.write(file_data)
            await grid_in.close()

            file_id = str(grid_in._id)
            logger.info(f"Stored logo in GridFS: {file_id}")
            return file_id

        except Exception as e:
            logger.error(f"Failed to store logo in GridFS: {e}")
            raise

    async def get_logo(self, file_id: str) -> Optional[bytes]:
        """
        Retrieve a logo from GridFS.

        Args:
            file_id: GridFS file ID

        Returns:
            Binary content of the logo or None if not found
        """
        try:
            grid_out = await self.logos_bucket.open_download_stream(ObjectId(file_id))
            data = await grid_out.read()
            return data
        except Exception as e:
            logger.warning(f"Failed to retrieve logo from GridFS: {e}")
            return None

    async def store_pdf(
        self,
        file_data: bytes,
        job_id: str,
        document_type: str = "invoice",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a generated PDF in GridFS.

        Args:
            file_data: Binary content of the PDF
            job_id: Job ID (used as filename)
            document_type: Type of document (invoice, infographic, formal)
            metadata: Additional metadata

        Returns:
            GridFS file ID as string
        """
        try:
            filename = f"{job_id}.pdf"
            file_metadata = {
                "job_id": job_id,
                "document_type": document_type,
                "content_type": "application/pdf",
                "generated_at": datetime.utcnow(),
                **(metadata or {})
            }

            grid_in = self.pdfs_bucket.open_upload_stream(
                filename=filename,
                metadata=file_metadata
            )

            await grid_in.write(file_data)
            await grid_in.close()

            file_id = str(grid_in._id)
            logger.info(f"Stored PDF in GridFS: {file_id} for job {job_id}")
            return file_id

        except Exception as e:
            logger.error(f"Failed to store PDF in GridFS: {e}")
            raise

    async def get_pdf(self, job_id: str) -> Optional[bytes]:
        """
        Retrieve a PDF from GridFS by job ID.

        Args:
            job_id: Job ID to search for

        Returns:
            Binary content of the PDF or None if not found
        """
        try:
            # Find the file by job_id in metadata
            cursor = self.pdfs_bucket.find({"metadata.job_id": job_id})
            async for grid_out in cursor:
                data = await grid_out.read()
                return data

            # Fallback: try to find by filename
            filename = f"{job_id}.pdf"
            cursor = self.pdfs_bucket.find({"filename": filename})
            async for grid_out in cursor:
                data = await grid_out.read()
                return data

            logger.warning(f"PDF not found in GridFS for job_id: {job_id}")
            return None

        except Exception as e:
            logger.error(f"Failed to retrieve PDF from GridFS: {e}")
            return None

    async def get_pdf_by_id(self, file_id: str) -> Optional[bytes]:
        """
        Retrieve a PDF from GridFS by file ID.

        Args:
            file_id: GridFS file ID

        Returns:
            Binary content of the PDF or None if not found
        """
        try:
            grid_out = await self.pdfs_bucket.open_download_stream(ObjectId(file_id))
            data = await grid_out.read()
            return data
        except Exception as e:
            logger.warning(f"Failed to retrieve PDF from GridFS by ID: {e}")
            return None

    async def delete_file(self, file_id: str, bucket: str = "pdfs") -> bool:
        """
        Delete a file from GridFS.

        Args:
            file_id: GridFS file ID
            bucket: Which bucket to delete from ("logos" or "pdfs")

        Returns:
            True if deleted successfully
        """
        try:
            target_bucket = self.pdfs_bucket if bucket == "pdfs" else self.logos_bucket
            await target_bucket.delete(ObjectId(file_id))
            logger.info(f"Deleted file from GridFS: {file_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to delete file from GridFS: {e}")
            return False

    async def get_file_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a stored PDF.

        Args:
            job_id: Job ID to search for

        Returns:
            File metadata or None if not found
        """
        try:
            cursor = self.pdfs_bucket.find({"metadata.job_id": job_id})
            async for grid_out in cursor:
                return {
                    "file_id": str(grid_out._id),
                    "filename": grid_out.filename,
                    "length": grid_out.length,
                    "upload_date": grid_out.upload_date,
                    "metadata": grid_out.metadata
                }
            return None
        except Exception as e:
            logger.warning(f"Failed to get file info from GridFS: {e}")
            return None
