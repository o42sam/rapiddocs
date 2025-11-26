"""
Invoice-specific schemas and data structures
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date


class InvoiceLineItem(BaseModel):
    """A single line item on an invoice"""
    description: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    amount: float = Field(..., ge=0)

    @property
    def calculated_amount(self) -> float:
        """Calculate the line item amount"""
        return self.quantity * self.unit_price


class InvoiceData(BaseModel):
    """Complete invoice data structure"""
    # Invoice metadata
    invoice_number: str = Field(..., min_length=1, max_length=50)
    invoice_date: str  # Changed from date to str to accept date strings
    due_date: str  # Changed from date to str to accept date strings

    # Billing information
    bill_from_name: str = Field(..., min_length=1, max_length=100)
    bill_from_address: Optional[str] = Field(None, max_length=300)
    bill_from_email: Optional[str] = Field(None, max_length=100)
    bill_from_phone: Optional[str] = Field(None, max_length=50)

    bill_to_name: str = Field(..., min_length=1, max_length=100)
    bill_to_address: Optional[str] = Field(None, max_length=300)
    bill_to_email: Optional[str] = Field(None, max_length=100)
    bill_to_phone: Optional[str] = Field(None, max_length=50)

    # Line items
    line_items: List[InvoiceLineItem] = Field(..., min_items=1, max_items=50)

    # Pricing
    subtotal: float = Field(..., ge=0)
    tax_rate: float = Field(0.0, ge=0, le=100)  # Percentage
    tax_amount: float = Field(0.0, ge=0)
    discount_amount: float = Field(0.0, ge=0)
    total: float = Field(..., ge=0)

    # Payment information
    payment_terms: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)

    @property
    def calculated_subtotal(self) -> float:
        """Calculate subtotal from line items"""
        return sum(item.calculated_amount for item in self.line_items)

    @property
    def calculated_tax(self) -> float:
        """Calculate tax amount"""
        return self.subtotal * (self.tax_rate / 100)

    @property
    def calculated_total(self) -> float:
        """Calculate final total"""
        return self.subtotal + self.calculated_tax - self.discount_amount
