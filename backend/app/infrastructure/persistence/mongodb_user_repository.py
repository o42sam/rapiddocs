"""
MongoDB User Repository Implementation.
Handles user persistence in MongoDB.
"""

import logging
from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
import bcrypt

from ...domain.interfaces.user_repository import IUserRepository
from ...domain.entities.user import User
from ...domain.exceptions import EntityNotFoundException, EntityExistsException

logger = logging.getLogger(__name__)


class MongoDBUserRepository(IUserRepository):
    """
    MongoDB implementation of user repository.

    This repository handles all user persistence operations
    using MongoDB as the storage backend.
    """

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize MongoDB user repository.

        Args:
            database: MongoDB database instance
        """
        self._db = database
        self._collection = self._db.users

    async def create_user(self, user: User) -> User:
        """
        Create a new user.

        Args:
            user: User entity to create

        Returns:
            Created user entity

        Raises:
            EntityExistsException: If user with email already exists
        """
        # Check if user exists
        existing = await self._collection.find_one({"email": user.email})
        if existing:
            raise EntityExistsException("User", user.email)

        # Convert to dict and insert
        user_dict = user.to_dict(include_sensitive=True)

        # Map password_hash to hashed_password for existing DB compatibility
        if "password_hash" in user_dict:
            user_dict["hashed_password"] = user_dict["password_hash"]
            # Keep both for now to support transition
            # del user_dict["password_hash"]

        # Ensure username field exists (existing DB uses this)
        if "name" in user_dict and "username" not in user_dict:
            user_dict["username"] = user_dict["name"]

        result = await self._collection.insert_one(user_dict)

        if not result.inserted_id:
            raise Exception("Failed to create user")

        logger.info(f"Created user: {user.id}")
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            User entity or None if not found
        """
        # Try both id field and MongoDB _id (converted from ObjectId string)
        from bson import ObjectId

        # First try the 'id' field
        user_dict = await self._collection.find_one({"id": user_id})

        # If not found, try _id as ObjectId
        if not user_dict:
            try:
                user_dict = await self._collection.find_one({"_id": ObjectId(user_id)})
            except:
                # If not a valid ObjectId format, just return None
                pass

        if not user_dict:
            return None

        return self._dict_to_user(user_dict)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            User entity or None if not found
        """
        user_dict = await self._collection.find_one({"email": email.lower()})
        if not user_dict:
            return None

        return self._dict_to_user(user_dict)

    async def update_user(self, user: User) -> User:
        """
        Update existing user.

        Args:
            user: User entity with updated data

        Returns:
            Updated user entity

        Raises:
            EntityNotFoundException: If user doesn't exist
        """
        from bson import ObjectId

        user.updated_at = datetime.utcnow()
        user_dict = user.to_dict(include_sensitive=True)

        # Map password_hash to hashed_password for existing DB compatibility
        if "password_hash" in user_dict:
            user_dict["hashed_password"] = user_dict["password_hash"]

        # Try updating by id field first, then by _id
        result = await self._collection.update_one(
            {"id": user.id},
            {"$set": user_dict}
        )

        # If no match, try with ObjectId
        if result.matched_count == 0:
            try:
                result = await self._collection.update_one(
                    {"_id": ObjectId(user.id)},
                    {"$set": user_dict}
                )
            except:
                pass

        if result.matched_count == 0:
            raise EntityNotFoundException("User", user.id)

        logger.info(f"Updated user: {user.id}")
        return user

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            True if deleted successfully

        Raises:
            EntityNotFoundException: If user doesn't exist
        """
        result = await self._collection.delete_one({"id": user_id})

        if result.deleted_count == 0:
            raise EntityNotFoundException("User", user_id)

        logger.info(f"Deleted user: {user_id}")
        return True

    async def list_users(
        self,
        limit: int = 100,
        offset: int = 0,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """
        List users with pagination.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            is_active: Filter by active status

        Returns:
            List of user entities
        """
        query = {}
        if is_active is not None:
            query["is_active"] = is_active

        cursor = self._collection.find(query).skip(offset).limit(limit)
        users = []

        async for user_dict in cursor:
            users.append(self._dict_to_user(user_dict))

        return users

    async def update_last_login(self, user_id: str) -> bool:
        """
        Update user's last login timestamp.

        Args:
            user_id: User's unique identifier

        Returns:
            True if updated successfully
        """
        from bson import ObjectId

        update_data = {
            "$set": {
                "last_login": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        }

        # Try updating by id field first
        result = await self._collection.update_one(
            {"id": user_id},
            update_data
        )

        # If no match, try with ObjectId
        if result.modified_count == 0:
            try:
                result = await self._collection.update_one(
                    {"_id": ObjectId(user_id)},
                    update_data
                )
            except:
                pass

        return result.modified_count > 0

    def _dict_to_user(self, user_dict: dict) -> User:
        """
        Convert dictionary to User entity.
        Handles both 'hashed_password' (existing DB) and 'password_hash' (new) fields.

        Args:
            user_dict: User data dictionary

        Returns:
            User entity
        """
        # Get username from either 'name' or 'username' field
        name = user_dict.get("name") or user_dict.get("username", "")

        user = User(
            email=user_dict["email"],
            name=name
        )

        # Set all fields - handle MongoDB _id
        if "id" in user_dict:
            user.id = user_dict["id"]
        elif "_id" in user_dict:
            # Convert ObjectId to string
            user.id = str(user_dict["_id"])
        else:
            # Generate new ID if needed
            from uuid import uuid4
            user.id = str(uuid4())

        # Handle both password field names - prefer hashed_password (existing DB schema)
        if "hashed_password" in user_dict:
            user.password_hash = user_dict["hashed_password"]
        elif "password_hash" in user_dict:
            user.password_hash = user_dict["password_hash"]
        elif "password" in user_dict:
            # Some records might have 'password' field
            user.password_hash = user_dict["password"]
        else:
            user.password_hash = ""

        # Handle date fields - they might be strings or datetime objects
        if "created_at" in user_dict:
            if isinstance(user_dict["created_at"], str):
                user.created_at = datetime.fromisoformat(user_dict["created_at"])
            else:
                user.created_at = user_dict["created_at"]

        if "updated_at" in user_dict:
            if isinstance(user_dict["updated_at"], str):
                user.updated_at = datetime.fromisoformat(user_dict["updated_at"])
            else:
                user.updated_at = user_dict["updated_at"]

        if user_dict.get("last_login"):
            if isinstance(user_dict["last_login"], str):
                user.last_login = datetime.fromisoformat(user_dict["last_login"])
            else:
                user.last_login = user_dict["last_login"]

        user.is_active = user_dict.get("is_active", True)
        user.is_verified = user_dict.get("is_verified", False)
        user.credits = user_dict.get("credits", 10)
        user.subscription_tier = user_dict.get("subscription_tier", "free")
        user.preferences = user_dict.get("preferences", {})
        user.refresh_token = user_dict.get("refresh_token")

        return user