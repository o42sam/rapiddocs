"""
Generation Job Entity.
Represents an asynchronous document generation job.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from uuid import uuid4


class JobStatus(Enum):
    """Status of a generation job."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class GenerationJob:
    """
    Generation job entity for tracking async document generation.

    Attributes:
        document_id: ID of the document being generated
        user_id: ID of the user who initiated the job
        job_type: Type of generation job
        status: Current job status
        id: Unique job identifier
        created_at: Job creation timestamp
        started_at: When job started processing
        completed_at: When job completed
        progress: Progress percentage (0-100)
        result: Job result data
        error: Error information if job failed
        retry_count: Number of retry attempts
        max_retries: Maximum retry attempts allowed
    """
    document_id: str
    user_id: str
    job_type: str
    status: JobStatus = JobStatus.QUEUED
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3

    def start(self) -> None:
        """Mark job as started."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.progress = 0

    def update_progress(self, progress: int) -> None:
        """
        Update job progress.

        Args:
            progress: Progress percentage (0-100)
        """
        self.progress = min(max(progress, 0), 100)

    def complete(self, result: Dict[str, Any]) -> None:
        """
        Mark job as completed.

        Args:
            result: Job result data
        """
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress = 100
        self.result = result
        self.error = None

    def fail(self, error_message: str, error_details: Optional[Dict] = None) -> None:
        """
        Mark job as failed.

        Args:
            error_message: Error message
            error_details: Additional error information
        """
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = {
            "message": error_message,
            "details": error_details or {},
            "timestamp": datetime.utcnow().isoformat()
        }

    def cancel(self) -> None:
        """Cancel the job."""
        if self.status in [JobStatus.QUEUED, JobStatus.RUNNING]:
            self.status = JobStatus.CANCELLED
            self.completed_at = datetime.utcnow()

    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return (
            self.status == JobStatus.FAILED and
            self.retry_count < self.max_retries
        )

    def retry(self) -> None:
        """Retry the job."""
        if self.can_retry():
            self.retry_count += 1
            self.status = JobStatus.QUEUED
            self.started_at = None
            self.completed_at = None
            self.progress = 0
            self.error = None

    @property
    def duration(self) -> Optional[float]:
        """Get job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_terminal(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in [
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "user_id": self.user_id,
            "job_type": self.job_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "duration": self.duration,
            "is_terminal": self.is_terminal
        }