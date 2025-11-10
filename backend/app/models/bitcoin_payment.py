"""
Bitcoin Payment Models
Database models for tracking Bitcoin payments and transactions.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class BitcoinPayment(BaseModel):
    """Model for Bitcoin payment transactions."""

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str  # User who initiated the payment
    package: str  # Package ID (small, medium, large)
    amount_usd: float  # Payment amount in USD
    amount_btc: float  # Payment amount in BTC
    credits: int  # Number of credits to be awarded

    # Bitcoin transaction details
    payment_address: str  # Generated Bitcoin address for this payment
    private_key_encrypted: str  # Encrypted private key for the payment address
    tx_hash: Optional[str] = None  # Transaction hash once payment is received

    # Payment status
    status: str = "pending"  # pending, confirming, confirmed, forwarded, failed, expired
    confirmations: int = 0  # Number of blockchain confirmations
    amount_received_btc: float = 0  # Actual amount received

    # Forwarding details
    forwarding_tx_hash: Optional[str] = None  # Transaction hash of forwarding to personal wallet
    forwarding_completed_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # When the payment request expires
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Additional metadata
    btc_usd_rate: float  # Exchange rate at time of payment creation
    network: str = "testnet"  # Bitcoin network (mainnet/testnet)
    error_message: Optional[str] = None  # Error message if payment failed

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "package": "medium",
                "amount_usd": 19.99,
                "amount_btc": 0.0005,
                "credits": 1000,
                "payment_address": "tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx",
                "status": "pending",
                "confirmations": 0,
                "btc_usd_rate": 40000.0,
                "network": "testnet"
            }
        }


class BitcoinPaymentStatus(BaseModel):
    """Response model for payment status checks."""

    payment_id: str
    status: str
    amount_btc: float
    amount_received_btc: float
    confirmations: int
    required_confirmations: int
    payment_address: str
    tx_hash: Optional[str]
    expires_at: datetime
    message: str
