"""
Invoice Entity.
Represents an invoice document with line items.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from uuid import uuid4


@dataclass
class LineItem:
    """
    Line item in an invoice.

    Attributes:
        description: Item description
        quantity: Number of items
        unit_price: Price per unit
        tax_rate: Tax rate as decimal (e.g., 0.1 for 10%)
        id: Unique identifier for the line item
    """
    description: str
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal = Decimal("0.0")
    id: str = field(default_factory=lambda: str(uuid4()))

    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal before tax."""
        return self.quantity * self.unit_price

    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        return self.subtotal * self.tax_rate

    @property
    def total(self) -> Decimal:
        """Calculate total including tax."""
        return self.subtotal + self.tax_amount

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "tax_rate": float(self.tax_rate),
            "subtotal": float(self.subtotal),
            "tax_amount": float(self.tax_amount),
            "total": float(self.total)
        }


@dataclass
class Invoice:
    """
    Invoice entity.

    Attributes:
        invoice_number: Unique invoice number
        client_name: Name of the client
        client_address: Client's address
        vendor_name: Name of the vendor/company
        vendor_address: Vendor's address
        line_items: List of invoice line items
        currency: Currency code (e.g., USD, EUR)
        issue_date: Date when invoice was issued
        due_date: Payment due date
        payment_terms: Payment terms text
        notes: Additional notes
        id: Unique identifier
    """
    invoice_number: str
    client_name: str
    client_address: str
    vendor_name: str
    vendor_address: str
    line_items: List[LineItem]
    currency: str = "USD"
    issue_date: datetime = field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    payment_terms: str = "Net 30"
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """Set default due date if not provided."""
        if self.due_date is None:
            # Default to 30 days from issue date
            self.due_date = self.issue_date + timedelta(days=30)

    @property
    def subtotal(self) -> Decimal:
        """Calculate invoice subtotal."""
        return sum(item.subtotal for item in self.line_items)

    @property
    def total_tax(self) -> Decimal:
        """Calculate total tax amount."""
        return sum(item.tax_amount for item in self.line_items)

    @property
    def total(self) -> Decimal:
        """Calculate invoice total."""
        return self.subtotal + self.total_tax

    def add_line_item(
        self,
        description: str,
        quantity: int,
        unit_price: Decimal,
        tax_rate: Decimal = Decimal("0.0")
    ) -> LineItem:
        """
        Add a line item to the invoice.

        Args:
            description: Item description
            quantity: Number of items
            unit_price: Price per unit
            tax_rate: Tax rate as decimal

        Returns:
            The created line item
        """
        item = LineItem(
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            tax_rate=tax_rate
        )
        self.line_items.append(item)
        return item

    def remove_line_item(self, item_id: str) -> bool:
        """
        Remove a line item by ID.

        Args:
            item_id: ID of the item to remove

        Returns:
            True if item was removed, False if not found
        """
        initial_count = len(self.line_items)
        self.line_items = [
            item for item in self.line_items if item.id != item_id
        ]
        return len(self.line_items) < initial_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "invoice_number": self.invoice_number,
            "client_name": self.client_name,
            "client_address": self.client_address,
            "vendor_name": self.vendor_name,
            "vendor_address": self.vendor_address,
            "line_items": [item.to_dict() for item in self.line_items],
            "currency": self.currency,
            "issue_date": self.issue_date.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "payment_terms": self.payment_terms,
            "notes": self.notes,
            "subtotal": float(self.subtotal),
            "total_tax": float(self.total_tax),
            "total": float(self.total)
        }