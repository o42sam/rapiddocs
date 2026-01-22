"""
ReportLab Table Generator Implementation.
Generates professional tables for invoices using ReportLab.
"""

from typing import List, Dict, Any, Optional
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from ...domain.interfaces.table_generator import ITableGenerator


class ReportLabTableGenerator(ITableGenerator):
    """
    ReportLab implementation of table generation for invoices.
    Creates professional-looking tables with customizable styling.
    """

    def __init__(self):
        """Initialize the table generator with default configurations."""
        self.column_widths: Optional[List[float]] = None
        self.default_style = self._create_default_style()

    def _create_default_style(self) -> Dict[str, Any]:
        """Create default table styling configuration."""
        return {
            "header_bg_color": colors.Color(0.25, 0.25, 0.25),  # Dark gray
            "header_text_color": colors.white,
            "row_bg_color": colors.white,
            "alt_row_bg_color": colors.Color(0.97, 0.97, 0.97),  # Light gray
            "border_color": colors.Color(0.85, 0.85, 0.85),
            "font_name": "Helvetica",
            "header_font_name": "Helvetica-Bold",
            "font_size": 9,
            "header_font_size": 10,
            "padding": 12,
            "header_padding": 10
        }

    def create_invoice_table(
        self,
        line_items: List[Dict[str, Any]],
        columns: List[str],
        style: Optional[Dict] = None
    ) -> Table:
        """
        Create invoice line items table.

        Args:
            line_items: List of invoice line item dictionaries
            columns: List of column names (e.g., ["#", "Description", "Qty", "Price", "Total"])
            style: Optional style configuration to override defaults

        Returns:
            ReportLab Table object
        """
        # Merge style with defaults
        table_style = {**self.default_style, **(style or {})}

        # Prepare table data
        table_data = [columns]  # Header row

        # Add line items
        for idx, item in enumerate(line_items, 1):
            row = []
            for col in columns:
                if col.lower() == "#" or col.lower() == "sl." or col.lower() == "no.":
                    row.append(str(idx))
                elif col.lower() == "description" or col.lower() == "item description":
                    row.append(item.get("description", ""))
                elif col.lower() == "quantity" or col.lower() == "qty" or col.lower() == "qty.":
                    row.append(str(item.get("quantity", 0)))
                elif col.lower() == "price" or col.lower() == "unit price":
                    price = item.get("unit_price", 0)
                    row.append(f"${price:.2f}")
                elif col.lower() == "total" or col.lower() == "amount":
                    total = item.get("total", item.get("quantity", 0) * item.get("unit_price", 0))
                    row.append(f"${total:.2f}")
                else:
                    row.append(str(item.get(col.lower(), "")))
            table_data.append(row)

        # Set column widths if not specified
        if self.column_widths is None:
            # Default widths for typical invoice columns
            if len(columns) == 5:  # Standard invoice format
                col_widths = [35, 230, 70, 70, 70]
            else:
                # Distribute evenly
                col_widths = [475 / len(columns)] * len(columns)
        else:
            col_widths = self.column_widths

        # Create table
        table = Table(table_data, colWidths=col_widths)

        # Apply styling
        table_style_commands = self._build_table_style(
            len(table_data),
            len(columns),
            table_style
        )
        table.setStyle(TableStyle(table_style_commands))

        return table

    def create_summary_table(
        self,
        subtotal: float,
        tax: float,
        total: float,
        currency: str = "USD"
    ) -> Table:
        """
        Create invoice summary table.

        Args:
            subtotal: Subtotal amount
            tax: Tax amount
            total: Total amount
            currency: Currency code

        Returns:
            ReportLab Table object for the summary
        """
        # Format currency symbol
        currency_symbol = self._get_currency_symbol(currency)

        # Create summary data
        summary_data = [
            ["Subtotal:", f"{currency_symbol}{subtotal:.2f}"],
            ["Tax:", f"{currency_symbol}{tax:.2f}"],
            ["", ""],  # Empty row for spacing
            ["Total:", f"{currency_symbol}{total:.2f}"]
        ]

        # Column widths for summary (right-aligned)
        col_widths = [100, 100]

        # Create table
        table = Table(summary_data, colWidths=col_widths)

        # Apply summary table styling
        style_commands = [
            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),

            # Font styling
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),

            # Text color
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0.2, 0.2, 0.2)),

            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),

            # Border for total row
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.Color(0.2, 0.2, 0.2)),
        ]

        table.setStyle(TableStyle(style_commands))

        return table

    def set_column_widths(self, widths: List[float]) -> None:
        """
        Set column widths for future tables.

        Args:
            widths: List of column widths in points
        """
        self.column_widths = widths

    def apply_style(self, style_config: Dict[str, Any]) -> None:
        """
        Apply styling configuration to future tables.

        Args:
            style_config: Dictionary containing style configuration
        """
        self.default_style.update(style_config)

    def _build_table_style(
        self,
        num_rows: int,
        num_cols: int,
        style: Dict[str, Any]
    ) -> List:
        """
        Build table style commands for ReportLab.

        Args:
            num_rows: Number of rows in the table
            num_cols: Number of columns in the table
            style: Style configuration dictionary

        Returns:
            List of TableStyle commands
        """
        commands = []

        # Header row styling
        commands.extend([
            ('BACKGROUND', (0, 0), (-1, 0), style["header_bg_color"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), style["header_text_color"]),
            ('FONTNAME', (0, 0), (-1, 0), style["header_font_name"]),
            ('FONTSIZE', (0, 0), (-1, 0), style["header_font_size"]),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), style["header_padding"]),
            ('BOTTOMPADDING', (0, 0), (-1, 0), style["header_padding"]),
        ])

        # Data rows styling
        commands.extend([
            ('FONTNAME', (0, 1), (-1, -1), style["font_name"]),
            ('FONTSIZE', (0, 1), (-1, -1), style["font_size"]),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.Color(0.2, 0.2, 0.2)),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # First column (index) centered
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Description column left-aligned
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'), # Other columns centered
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), style["padding"]),
            ('BOTTOMPADDING', (0, 1), (-1, -1), style["padding"]),
        ])

        # Alternating row colors
        for i in range(1, num_rows):
            if i % 2 == 0:
                commands.append(
                    ('BACKGROUND', (0, i), (-1, i), style["alt_row_bg_color"])
                )
            else:
                commands.append(
                    ('BACKGROUND', (0, i), (-1, i), style["row_bg_color"])
                )

        # Grid lines
        commands.extend([
            ('LINEBELOW', (0, 0), (-1, 0), 1, style["header_bg_color"]),
            ('LINEBELOW', (0, 1), (-1, -2), 0.5, style["border_color"]),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, style["border_color"]),
        ])

        return commands

    def _get_currency_symbol(self, currency: str) -> str:
        """
        Get currency symbol from currency code.

        Args:
            currency: Currency code (e.g., "USD", "EUR", "GBP")

        Returns:
            Currency symbol
        """
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CNY": "¥",
            "INR": "₹",
            "CAD": "C$",
            "AUD": "A$",
            "CHF": "Fr.",
            "SEK": "kr",
            "NOK": "kr",
            "DKK": "kr",
            "NGN": "₦",
            "ZAR": "R",
            "BRL": "R$",
            "MXN": "$",
        }
        return currency_symbols.get(currency, currency + " ")