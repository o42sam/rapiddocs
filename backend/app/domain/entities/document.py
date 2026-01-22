"""
Document Entity.
Core business entity representing a document.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from uuid import uuid4


class DocumentType(Enum):
    """Types of documents that can be generated."""
    INVOICE = "invoice"
    INFOGRAPHIC = "infographic"
    FORMAL = "formal"


class DocumentStatus(Enum):
    """Status of document generation."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Document:
    """
    Document entity representing a generated document.

    Attributes:
        id: Unique identifier for the document
        type: Type of document (invoice, infographic, formal)
        status: Current generation status
        user_id: ID of the user who created the document
        title: Document title
        metadata: Additional document metadata
        file_path: Path to the generated document file
        created_at: Timestamp when document was created
        updated_at: Timestamp of last update
        error_message: Error message if generation failed
    """
    type: DocumentType
    user_id: str
    title: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: DocumentStatus = DocumentStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None

    def mark_processing(self) -> None:
        """Mark document as being processed."""
        self.status = DocumentStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_completed(self, file_path: str) -> None:
        """
        Mark document as completed.

        Args:
            file_path: Path to the generated document file
        """
        self.status = DocumentStatus.COMPLETED
        self.file_path = file_path
        self.updated_at = datetime.utcnow()
        self.error_message = None

    def mark_failed(self, error_message: str) -> None:
        """
        Mark document as failed.

        Args:
            error_message: Description of the failure
        """
        self.status = DocumentStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.utcnow()

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the document.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type.value,
            "status": self.status.value,
            "user_id": self.user_id,
            "title": self.title,
            "metadata": self.metadata,
            "file_path": self.file_path,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error_message": self.error_message
        }