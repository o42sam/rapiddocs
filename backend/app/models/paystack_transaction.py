"""
Paystack transaction models for tracking all payment types
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.document import PyObjectId


class PaystackTransaction(BaseModel):
    """Model for tracking Paystack transactions"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str  # User who initiated the transaction

    # Transaction identifiers
    reference: str = Field(..., description="Unique transaction reference")
    paystack_reference: Optional[str] = Field(None, description="Paystack's transaction reference")

    # Payment details
    payment_method: str = Field(..., description="card, bank_transfer, etc.")
    amount: float = Field(..., gt=0, description="Amount in kobo (for NGN) or smallest currency unit")
    currency: str = Field(default="NGN", description="Currency code")

    # Credits purchase info
    credits_package_id: Optional[str] = None
    credits_amount: int = Field(..., gt=0, description="Number of credits to be added")

    # Status tracking
    status: str = Field(
        default="pending",
        description="pending, success, failed, abandoned, cancelled"
    )

    # Card payment specific
    authorization_url: Optional[str] = None  # URL to redirect user for card payment
    access_code: Optional[str] = None  # Paystack access code

    # Virtual account specific (for bank transfer)
    virtual_account_id: Optional[str] = None  # Paystack dedicated virtual account ID
    account_number: Optional[str] = None  # Generated account number
    bank_name: Optional[str] = None  # Bank providing the account
    account_name: Optional[str] = None  # Account name for transfers

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Payment gateway response
    gateway_response: Optional[str] = None
    gateway_response_code: Optional[str] = None

    # IP and user agent for fraud detection
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None  # When payment was confirmed
    expires_at: Optional[datetime] = None  # For virtual accounts

    # Webhook verification
    webhook_received: bool = False
    webhook_verified: bool = False

    # Error tracking
    error_message: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PaystackVirtualAccount(BaseModel):
    """Model for Paystack dedicated virtual accounts"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str

    # Paystack virtual account details
    paystack_id: str = Field(..., description="Paystack dedicated account ID")
    account_number: str
    bank_name: str
    bank_slug: str  # e.g., 'wema-bank'
    account_name: str

    # Assignment
    assigned: bool = Field(default=True)
    active: bool = Field(default=True)

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PaystackWebhookLog(BaseModel):
    """Model for logging all webhook events from Paystack"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    # Event details
    event_type: str  # charge.success, transfer.success, etc.
    event_data: Dict[str, Any]

    # Verification
    signature: str
    verified: bool = False

    # Processing
    processed: bool = False
    processing_error: Optional[str] = None

    # Reference to transaction
    transaction_reference: Optional[str] = None

    # Timestamps
    received_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
