"""
Data Importer Interface.
Defines the contract for importing data from external files.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path


class IDataImporter(ABC):
    """
    Interface for importing data from external files.
    Implementations: CSV importer, Excel importer
    """

    @abstractmethod
    async def import_file(
        self,
        file_path: Path,
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Import data from file.

        Args:
            file_path: Path to the file to import
            options: Optional import options

        Returns:
            List of dictionaries containing imported data
        """
        pass

    @abstractmethod
    async def validate_file(
        self,
        file_path: Path,
        expected_columns: Optional[List[str]] = None
    ) -> bool:
        """
        Validate file format and structure.

        Args:
            file_path: Path to the file to validate
            expected_columns: Optional list of expected column names

        Returns:
            True if file is valid, False otherwise
        """
        pass

    @abstractmethod
    def preview(
        self,
        file_path: Path,
        rows: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Preview first N rows of data.

        Args:
            file_path: Path to the file to preview
            rows: Number of rows to preview

        Returns:
            List of preview data dictionaries
        """
        pass

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        pass