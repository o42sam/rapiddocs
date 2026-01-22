"""
MongoDB Document Repository Implementation.
Stores document metadata in MongoDB.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from ...domain.interfaces.document_repository import IDocumentRepository
from ...domain.exceptions import RepositoryException
from .database import get_database

logger = logging.getLogger(__name__)


class MongoDBDocumentRepository(IDocumentRepository):
    """
    MongoDB implementation of document repository.
    """

    def __init__(self, database: Optional[AsyncIOMotorDatabase] = None):
        """
        Initialize MongoDB document repository.

        Args:
            database: MongoDB database instance
        """
        self._db = database
        self._collection_name = "documents"

    async def _get_collection(self):
        """Get documents collection."""
        if not self._db:
            self._db = get_database()
        return self._db[self._collection_name] if self._db else None

    async def save_document(
        self,
        document_id: str,
        document_data: Dict[str, Any],
        user_id: str
    ) -> str:
        """
        Save document metadata.

        Args:
            document_id: Document ID
            document_data: Document metadata
            user_id: User ID

        Returns:
            Document ID
        """
        try:
            collection = await self._get_collection()
            if not collection:
                # Fallback to in-memory storage
                logger.warning("MongoDB not available, document metadata not persisted")
                return document_id

            document = {
                "_id": document_id,
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                **document_data
            }

            await collection.replace_one(
                {"_id": document_id},
                document,
                upsert=True
            )

            logger.info(f"Document {document_id} saved successfully")
            return document_id

        except PyMongoError as e:
            logger.error(f"Failed to save document: {e}")
            raise RepositoryException(f"Failed to save document: {str(e)}")

    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document data or None
        """
        try:
            collection = await self._get_collection()
            if not collection:
                return None

            document = await collection.find_one({"_id": document_id})
            return document

        except PyMongoError as e:
            logger.error(f"Failed to get document: {e}")
            raise RepositoryException(f"Failed to get document: {str(e)}")

    async def get_user_documents(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get documents by user ID.

        Args:
            user_id: User ID
            limit: Maximum number of documents
            offset: Offset for pagination

        Returns:
            List of documents
        """
        try:
            collection = await self._get_collection()
            if not collection:
                return []

            cursor = collection.find({"user_id": user_id})\
                .sort("created_at", -1)\
                .skip(offset)\
                .limit(limit)

            documents = await cursor.to_list(length=limit)
            return documents

        except PyMongoError as e:
            logger.error(f"Failed to get user documents: {e}")
            raise RepositoryException(f"Failed to get user documents: {str(e)}")

    async def update_document_status(
        self,
        document_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update document status.

        Args:
            document_id: Document ID
            status: New status
            error_message: Error message if failed

        Returns:
            True if updated successfully
        """
        try:
            collection = await self._get_collection()
            if not collection:
                return False

            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }

            if error_message:
                update_data["error_message"] = error_message

            result = await collection.update_one(
                {"_id": document_id},
                {"$set": update_data}
            )

            return result.modified_count > 0

        except PyMongoError as e:
            logger.error(f"Failed to update document status: {e}")
            raise RepositoryException(f"Failed to update document status: {str(e)}")

    async def delete_document(self, document_id: str) -> bool:
        """
        Delete document.

        Args:
            document_id: Document ID

        Returns:
            True if deleted successfully
        """
        try:
            collection = await self._get_collection()
            if not collection:
                return False

            result = await collection.delete_one({"_id": document_id})
            return result.deleted_count > 0

        except PyMongoError as e:
            logger.error(f"Failed to delete document: {e}")
            raise RepositoryException(f"Failed to delete document: {str(e)}")