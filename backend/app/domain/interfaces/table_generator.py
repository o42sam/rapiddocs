"""
Table Generator Interface.
Defines the contract for table generation (primarily for invoices).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class ITableGenerator(ABC):
    """
    Interface for table generation (primarily for invoices).
    Implementations: ReportLab tables, HTML tables, Markdown tables
    """

    @abstractmethod
    def create_invoice_table(
        self,
        line_items: List[Dict[str, Any]],
        columns: List[str],
        style: Optional[Dict] = None
    ) -> Any:
        """
        Create invoice line items table.

        Args:
            line_items: List of invoice line item dictionaries
            columns: List of column names
            style: Optional style configuration

        Returns:
            Table object (implementation-specific)
        """
        pass

    @abstractmethod
    def create_summary_table(
        self,
        subtotal: float,
        tax: float,
        total: float,
        currency: str = "USD"
    ) -> Any:
        """
        Create invoice summary table.

        Args:
            subtotal: Subtotal amount
            tax: Tax amount
            total: Total amount
            currency: Currency code

        Returns:
            Summary table object (implementation-specific)
        """
        pass

    @abstractmethod
    def set_column_widths(self, widths: List[float]) -> None:
        """
        Set column widths.

        Args:
            widths: List of column widths in points or percentages
        """
        pass

    @abstractmethod
    def apply_style(self, style_config: Dict[str, Any]) -> None:
        """
        Apply styling to table.

        Args:
            style_config: Dictionary containing style configuration
        """
        pass