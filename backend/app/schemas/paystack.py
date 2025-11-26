"""
Paystack payment schemas for API requests and responses
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


# Request schemas
class InitializeCardPaymentRequest(BaseModel):
    """Request to initialize a card payment"""
    email: EmailStr
    amount: float = Field(..., gt=0, description="Amount in NGN (will be converted to kobo)")
    credits_package_id: str = Field(..., description="ID of credits package being purchased")
    callback_url: Optional[str] = Field(None, description="URL to redirect after payment")


class InitializeVirtualAccountRequest(BaseModel):
    """Request to create a dedicated virtual account for bank transfer"""
    email: EmailStr
    amount: float = Field(..., gt=0, description="Amount in NGN (will be converted to kobo)")
    credits_package_id: str = Field(..., description="ID of credits package being purchased")
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, description="Phone number for notifications")
    preferred_bank: Optional[str] = Field("wema-bank", description="Preferred bank slug")


class VerifyPaymentRequest(BaseModel):
    """Request to verify a payment"""
    reference: str = Field(..., description="Transaction reference")


# Response schemas
class InitializeCardPaymentResponse(BaseModel):
    """Response after initializing card payment"""
    status: str
    message: str
    reference: str
    authorization_url: str
    access_code: str


class VirtualAccountResponse(BaseModel):
    """Response with virtual account details"""
    status: str
    message: str
    reference: str
    account_number: str
    bank_name: str
    account_name: str
    amount: float
    expires_at: Optional[str] = None


class PaymentVerificationResponse(BaseModel):
    """Response after verifying payment"""
    status: str
    message: str
    reference: str
    amount: float
    credits_added: int
    payment_status: str  # success, pending, failed
    paid_at: Optional[str] = None


class TransactionResponse(BaseModel):
    """Transaction details response"""
    id: str
    reference: str
    amount: float
    currency: str
    status: str
    payment_method: str
    credits_amount: int
    created_at: str
    paid_at: Optional[str] = None


class PaystackWebhookEvent(BaseModel):
    """Paystack webhook event payload"""
    event: str
    data: Dict[str, Any]


# Internal schemas for Paystack API responses
class PaystackInitializeResponse(BaseModel):
    """Paystack API response for initialization"""
    status: bool
    message: str
    data: Dict[str, Any]


class PaystackVerifyResponse(BaseModel):
    """Paystack API response for verification"""
    status: bool
    message: str
    data: Dict[str, Any]


class PaystackDedicatedAccountResponse(BaseModel):
    """Paystack API response for dedicated virtual account"""
    status: bool
    message: str
    data: Dict[str, Any]
