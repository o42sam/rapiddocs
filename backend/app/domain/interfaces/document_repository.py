"""
Document Repository Interface.
Defines the contract for document persistence operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime


class IDocumentRepository(ABC):
    """
    Interface for document storage and retrieval.
    Implementations: MongoDB, PostgreSQL, File System
    """

    @abstractmethod
    async def save_document(
        self,
        document_id: str,
        document_data: Dict[str, Any],
        user_id: str
    ) -> str:
        """
        Save document metadata to repository.

        Args:
            document_id: Unique document identifier
            document_data: Document metadata dictionary
            user_id: ID of the user who created the document

        Returns:
            Document ID
        """
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve document metadata by ID.

        Args:
            document_id: Document identifier

        Returns:
            Document metadata dictionary or None if not found
        """
        pass

    @abstractmethod
    async def list_documents(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List documents for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of documents to return
            offset: Number of documents to skip

        Returns:
            List of document metadata dictionaries
        """
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete document from repository.

        Args:
            document_id: Document identifier

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def update_document_status(
        self,
        document_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update document generation status.

        Args:
            document_id: Document identifier
            status: New status (pending, processing, completed, failed)
            error_message: Optional error message if failed

        Returns:
            True if updated successfully, False otherwise
        """
        pass