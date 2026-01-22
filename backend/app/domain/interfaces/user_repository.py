"""
User Repository Interface.
Defines the contract for user persistence operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ..entities.user import User


class IUserRepository(ABC):
    """
    Interface for user repository.
    Handles user persistence and retrieval.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            User entity or None if not found
        """
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            User entity or None if not found
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def update_last_login(self, user_id: str) -> bool:
        """
        Update user's last login timestamp.

        Args:
            user_id: User's unique identifier

        Returns:
            True if updated successfully
        """
        pass