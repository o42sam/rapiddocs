"""
Bitcoin Payment Schemas
Pydantic schemas for Bitcoin payment API requests and responses.
"""

from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class BitcoinPaymentInitRequest(BaseModel):
    """Request to initiate a Bitcoin payment."""
    package: Literal["small", "medium", "large"]


class BitcoinPaymentInitResponse(BaseModel):
    """Response after initiating a Bitcoin payment."""
    payment_id: str
    payment_address: str
    amount_btc: float
    amount_usd: float
    qr_code_data: str  # Base64 encoded QR code image
    expires_at: datetime
    message: str


class BitcoinPaymentStatusRequest(BaseModel):
    """Request to check payment status."""
    payment_id: str


class BitcoinPaymentStatusResponse(BaseModel):
    """Response for payment status check."""
    payment_id: str
    status: str  # pending, confirming, confirmed, forwarded, failed, expired
    payment_address: str
    amount_btc: float
    amount_received_btc: float
    amount_usd: float
    confirmations: int
    required_confirmations: int
    tx_hash: Optional[str] = None
    forwarding_tx_hash: Optional[str] = None
    expires_at: datetime
    credits: int
    message: str


class BitcoinPaymentConfirmResponse(BaseModel):
    """Response after confirming and processing a payment."""
    success: bool
    payment_id: str
    credits_added: int
    new_balance: int
    tx_hash: str
    message: str
