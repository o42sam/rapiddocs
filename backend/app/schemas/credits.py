from typing import Literal
from pydantic import BaseModel, Field


class CreditsPurchaseRequest(BaseModel):
    """Schema for credits purchase request"""
    package: Literal["small", "medium", "large"]
    bitcoin_transaction_id: str = Field(..., min_length=10, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "package": "small",
                "bitcoin_transaction_id": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
            }
        }


class CreditsPurchaseResponse(BaseModel):
    """Schema for credits purchase response"""
    message: str
    credits_added: int
    new_balance: int
    transaction_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Credits purchased successfully",
                "credits_added": 400,
                "new_balance": 440,
                "transaction_id": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
            }
        }


class CreditsBalanceResponse(BaseModel):
    """Schema for credits balance response"""
    credits: int
    user_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "credits": 40,
                "user_id": "507f1f77bcf86cd799439011"
            }
        }


class CreditsPackage(BaseModel):
    """Schema for credits package information"""
    id: str
    name: str
    credits: int
    price: float
    currency: str = "USD"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "small",
                "name": "Small Package",
                "credits": 400,
                "price": 9.99,
                "currency": "USD"
            }
        }


class CreditsPackagesResponse(BaseModel):
    """Schema for available credits packages"""
    packages: list[CreditsPackage]

    class Config:
        json_schema_extra = {
            "example": {
                "packages": [
                    {
                        "id": "small",
                        "name": "Small Package",
                        "credits": 400,
                        "price": 9.99,
                        "currency": "USD"
                    },
                    {
                        "id": "medium",
                        "name": "Medium Package",
                        "credits": 1000,
                        "price": 19.99,
                        "currency": "USD"
                    },
                    {
                        "id": "large",
                        "name": "Large Package",
                        "credits": 10000,
                        "price": 59.99,
                        "currency": "USD"
                    }
                ]
            }
        }
