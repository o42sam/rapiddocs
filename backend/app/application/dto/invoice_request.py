"""
Invoice Request DTO.
Data transfer object for invoice generation requests.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


@dataclass
class InvoiceLineItemDTO:
    """DTO for invoice line items."""
    description: str
    quantity: int
    unit_price: float
    tax_rate: float = 0.0


@dataclass
class InvoiceRequest:
    """
    DTO for invoice generation request.

    Attributes:
        invoice_number: Unique invoice number
        client_name: Client name
        client_address: Client address
        vendor_name: Vendor/company name
        vendor_address: Vendor address
        line_items: List of line items
        currency: Currency code
        logo_path: Optional path to logo file
        output_format: Output format (pdf, docx, html, md)
        ai_generate_terms: Whether to AI-generate payment terms
        ai_generate_notes: Whether to AI-generate invoice notes
        custom_terms: Custom payment terms (if not AI-generated)
        custom_notes: Custom notes (if not AI-generated)
        color_scheme: List of hex color codes
        import_file_path: Optional path to CSV/Excel file for line items
        user_id: ID of requesting user
    """
    invoice_number: str
    client_name: str
    client_address: str
    vendor_name: str
    vendor_address: str
    line_items: List[InvoiceLineItemDTO]
    currency: str = "USD"
    logo_path: Optional[str] = None
    output_format: str = "pdf"
    ai_generate_terms: bool = True
    ai_generate_notes: bool = True
    custom_terms: Optional[str] = None
    custom_notes: Optional[str] = None
    color_scheme: List[str] = None
    import_file_path: Optional[str] = None
    user_id: Optional[str] = None

    def __post_init__(self):
        """Set default color scheme if not provided."""
        if self.color_scheme is None:
            self.color_scheme = ["#1e40af", "#3730a3", "#7c3aed"]

    def validate(self) -> List[str]:
        """
        Validate the request.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.invoice_number:
            errors.append("Invoice number is required")
        if not self.client_name:
            errors.append("Client name is required")
        if not self.vendor_name:
            errors.append("Vendor name is required")
        if not self.line_items and not self.import_file_path:
            errors.append("Line items or import file path is required")

        for item in self.line_items:
            if item.quantity <= 0:
                errors.append(f"Invalid quantity for item: {item.description}")
            if item.unit_price < 0:
                errors.append(f"Invalid unit price for item: {item.description}")
            if not 0 <= item.tax_rate <= 1:
                errors.append(f"Tax rate must be between 0 and 1 for item: {item.description}")

        valid_formats = ["pdf", "docx", "html", "md"]
        if self.output_format not in valid_formats:
            errors.append(f"Invalid output format. Must be one of: {', '.join(valid_formats)}")

        for color in self.color_scheme:
            if not color.startswith("#") or len(color) != 7:
                errors.append(f"Invalid color code: {color}")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "invoice_number": self.invoice_number,
            "client_name": self.client_name,
            "client_address": self.client_address,
            "vendor_name": self.vendor_name,
            "vendor_address": self.vendor_address,
            "line_items": [
                {
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "tax_rate": item.tax_rate
                }
                for item in self.line_items
            ],
            "currency": self.currency,
            "logo_path": self.logo_path,
            "output_format": self.output_format,
            "ai_generate_terms": self.ai_generate_terms,
            "ai_generate_notes": self.ai_generate_notes,
            "custom_terms": self.custom_terms,
            "custom_notes": self.custom_notes,
            "color_scheme": self.color_scheme,
            "import_file_path": self.import_file_path,
            "user_id": self.user_id
        }