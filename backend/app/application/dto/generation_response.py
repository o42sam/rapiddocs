"""
Generation Response DTOs.
Response data transfer objects for document generation.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class GenerationResponse:
    """
    Response DTO for document generation.

    Attributes:
        document_id: Unique document identifier
        job_id: Generation job identifier
        status: Current status
        message: Status message
        download_url: URL to download the document (when completed)
        created_at: Creation timestamp
        error: Error details if failed
    """
    document_id: str
    job_id: str
    status: str
    message: str
    download_url: Optional[str] = None
    created_at: Optional[datetime] = None
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "job_id": self.job_id,
            "status": self.status,
            "message": self.message,
            "download_url": self.download_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "error": self.error
        }


@dataclass
class JobResponse:
    """
    Response DTO for job status check.

    Attributes:
        job_id: Job identifier
        document_id: Document identifier
        status: Current job status
        progress: Progress percentage (0-100)
        result: Job result (when completed)
        error: Error details if failed
        created_at: Job creation timestamp
        completed_at: Job completion timestamp
    """
    job_id: str
    document_id: str
    status: str
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_id": self.job_id,
            "document_id": self.document_id,
            "status": self.status,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }