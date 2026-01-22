"""
In-Memory User Repository Implementation.
For testing and development without database.
"""

import logging
from typing import Optional, List, Dict
from datetime import datetime

from ...domain.interfaces.user_repository import IUserRepository
from ...domain.entities.user import User
from ...domain.exceptions import EntityNotFoundException, EntityExistsException

logger = logging.getLogger(__name__)


class InMemoryUserRepository(IUserRepository):
    """
    In-memory implementation of user repository.

    This repository stores users in memory for testing
    and development purposes.
    """

    def __init__(self):
        """Initialize in-memory user repository."""
        self._users: Dict[str, User] = {}
        self._email_index: Dict[str, str] = {}  # email -> user_id mapping

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
        if user.email.lower() in self._email_index:
            raise EntityExistsException("User", user.email)

        # Store user
        self._users[user.id] = user
        self._email_index[user.email.lower()] = user.id

        logger.info(f"Created user in memory: {user.id}")
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            User entity or None if not found
        """
        return self._users.get(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            User entity or None if not found
        """
        user_id = self._email_index.get(email.lower())
        if user_id:
            return self._users.get(user_id)
        return None

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
        if user.id not in self._users:
            raise EntityNotFoundException("User", user.id)

        user.updated_at = datetime.utcnow()
        self._users[user.id] = user

        logger.info(f"Updated user in memory: {user.id}")
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
        if user_id not in self._users:
            raise EntityNotFoundException("User", user_id)

        user = self._users[user_id]
        del self._users[user_id]
        del self._email_index[user.email.lower()]

        logger.info(f"Deleted user from memory: {user_id}")
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
        users = list(self._users.values())

        # Filter by active status if specified
        if is_active is not None:
            users = [u for u in users if u.is_active == is_active]

        # Sort by creation date
        users.sort(key=lambda u: u.created_at, reverse=True)

        # Apply pagination
        return users[offset:offset + limit]

    async def update_last_login(self, user_id: str) -> bool:
        """
        Update user's last login timestamp.

        Args:
            user_id: User's unique identifier

        Returns:
            True if updated successfully
        """
        if user_id in self._users:
            user = self._users[user_id]
            user.last_login = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            return True
        return False