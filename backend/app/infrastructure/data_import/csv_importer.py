"""
CSV Data Importer Implementation.
Implements IDataImporter interface for CSV files.
"""

import csv
from typing import List, Dict, Any, Optional
from pathlib import Path

from ...domain.interfaces.data_importer import IDataImporter
from ...shared.logger import get_logger

logger = get_logger("csv_importer")


class CSVImporter(IDataImporter):
    """
    CSV implementation of data importer.
    Imports statistics and other data from CSV files.

    Expected columns for infographic:
    - name: Statistic name
    - value: Numeric value
    - unit: Unit of measurement
    - visualization_type: Chart type (bar_chart, line_chart, pie_chart, gauge_chart, number)
    - category: Optional category for grouping
    - description: Optional description
    """

    # Expected column names (flexible matching)
    COLUMN_ALIASES = {
        'name': ['name', 'label', 'title', 'statistic', 'stat_name'],
        'value': ['value', 'amount', 'number', 'quantity', 'stat_value'],
        'unit': ['unit', 'units', 'measurement', 'uom'],
        'visualization_type': ['visualization_type', 'viz_type', 'chart_type', 'chart', 'type'],
        'category': ['category', 'group', 'cat'],
        'description': ['description', 'desc', 'details', 'notes']
    }

    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialize the CSV importer.

        Args:
            encoding: File encoding (default: utf-8)
        """
        self._encoding = encoding
        logger.info("CSV Importer initialized")

    @property
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        return ['.csv']

    async def import_file(
        self,
        file_path: Path,
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Import data from CSV file.

        Args:
            file_path: Path to the CSV file
            options: Optional import options
                - delimiter: CSV delimiter (default: ',')
                - skip_rows: Number of rows to skip
                - encoding: File encoding

        Returns:
            List of dictionaries containing imported data
        """
        logger.info(f"Importing CSV file: {file_path}")

        options = options or {}
        delimiter = options.get('delimiter', ',')
        skip_rows = options.get('skip_rows', 0)
        encoding = options.get('encoding', self._encoding)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        try:
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                # Skip specified rows
                for _ in range(skip_rows):
                    next(f)

                reader = csv.DictReader(f, delimiter=delimiter)

                # Map columns to standard names
                column_mapping = self._create_column_mapping(reader.fieldnames or [])
                logger.debug(f"Column mapping: {column_mapping}")

                data = []
                for row in reader:
                    try:
                        mapped_row = self._map_row(row, column_mapping)
                        if self._validate_row(mapped_row):
                            data.append(mapped_row)
                    except Exception as e:
                        logger.warning(f"Skipping invalid row: {e}")
                        continue

            logger.info(f"Imported {len(data)} records from CSV")
            return data

        except Exception as e:
            logger.error(f"Failed to import CSV: {e}")
            raise

    async def validate_file(
        self,
        file_path: Path,
        expected_columns: Optional[List[str]] = None
    ) -> bool:
        """
        Validate CSV file format and structure.

        Args:
            file_path: Path to the file to validate
            expected_columns: Optional list of expected column names

        Returns:
            True if file is valid, False otherwise
        """
        logger.info(f"Validating CSV file: {file_path}")

        if not file_path.exists():
            logger.error("File does not exist")
            return False

        if file_path.suffix.lower() not in self.supported_extensions:
            logger.error(f"Invalid file extension: {file_path.suffix}")
            return False

        try:
            with open(file_path, 'r', encoding=self._encoding, newline='') as f:
                reader = csv.DictReader(f)

                # Check headers
                if not reader.fieldnames:
                    logger.error("No headers found in CSV")
                    return False

                # Validate expected columns if provided
                if expected_columns:
                    column_mapping = self._create_column_mapping(reader.fieldnames)
                    for expected in expected_columns:
                        if expected not in column_mapping:
                            logger.warning(f"Missing expected column: {expected}")
                            return False

                # Try to read first row
                try:
                    next(reader)
                except StopIteration:
                    logger.warning("CSV file has no data rows")
                    # File is valid but empty
                    return True

            logger.info("CSV file validation passed")
            return True

        except Exception as e:
            logger.error(f"CSV validation failed: {e}")
            return False

    def preview(
        self,
        file_path: Path,
        rows: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Preview first N rows of CSV data.

        Args:
            file_path: Path to the file to preview
            rows: Number of rows to preview

        Returns:
            List of preview data dictionaries
        """
        logger.info(f"Previewing CSV file: {file_path} (first {rows} rows)")

        if not file_path.exists():
            return []

        try:
            with open(file_path, 'r', encoding=self._encoding, newline='') as f:
                reader = csv.DictReader(f)

                column_mapping = self._create_column_mapping(reader.fieldnames or [])
                preview_data = []

                for i, row in enumerate(reader):
                    if i >= rows:
                        break
                    try:
                        mapped_row = self._map_row(row, column_mapping)
                        preview_data.append(mapped_row)
                    except Exception:
                        continue

            return preview_data

        except Exception as e:
            logger.error(f"Preview failed: {e}")
            return []

    def _create_column_mapping(self, headers: List[str]) -> Dict[str, str]:
        """
        Create mapping from standard names to actual column names.

        Args:
            headers: List of actual column headers

        Returns:
            Dictionary mapping standard names to actual column names
        """
        mapping = {}
        headers_lower = {h.lower().strip(): h for h in headers}

        for standard_name, aliases in self.COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in headers_lower:
                    mapping[standard_name] = headers_lower[alias]
                    break

        return mapping

    def _map_row(
        self,
        row: Dict[str, Any],
        column_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Map a row to standard column names.

        Args:
            row: Original row data
            column_mapping: Column name mapping

        Returns:
            Mapped row dictionary
        """
        mapped = {}

        # Map each standard column
        for standard_name, actual_name in column_mapping.items():
            value = row.get(actual_name, '')

            # Type conversion
            if standard_name == 'value':
                try:
                    # Handle numeric values
                    value = value.replace(',', '').strip()
                    mapped[standard_name] = float(value) if value else 0.0
                except ValueError:
                    mapped[standard_name] = 0.0
            else:
                mapped[standard_name] = str(value).strip() if value else ''

        # Set defaults for missing fields
        if 'name' not in mapped or not mapped['name']:
            mapped['name'] = 'Unnamed'
        if 'value' not in mapped:
            mapped['value'] = 0.0
        if 'unit' not in mapped or not mapped['unit']:
            mapped['unit'] = 'units'
        if 'visualization_type' not in mapped or not mapped['visualization_type']:
            mapped['visualization_type'] = 'bar_chart'

        return mapped

    def _validate_row(self, row: Dict[str, Any]) -> bool:
        """
        Validate a mapped row.

        Args:
            row: Mapped row dictionary

        Returns:
            True if row is valid
        """
        # Must have a name
        if not row.get('name'):
            return False

        # Value must be numeric
        try:
            float(row.get('value', 0))
        except (ValueError, TypeError):
            return False

        # Validate visualization type
        valid_types = ['bar_chart', 'line_chart', 'pie_chart', 'gauge_chart', 'number']
        viz_type = row.get('visualization_type', 'bar_chart').lower()
        if viz_type not in valid_types:
            row['visualization_type'] = 'bar_chart'

        return True

    def get_status(self) -> Dict[str, Any]:
        """Get importer status information."""
        return {
            "importer": "CSVImporter",
            "supported_extensions": self.supported_extensions,
            "encoding": self._encoding
        }
