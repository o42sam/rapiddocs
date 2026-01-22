"""
Credits API Routes.
Handles credit management for document generation.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/balance")
async def get_credit_balance() -> Dict[str, Any]:
    """
    Get current credit balance.
    For now, returns unlimited credits for development.
    """
    return {
        "credits": 1000,
        "message": "Development mode - unlimited credits"
    }


@router.post("/deduct")
async def deduct_credits(
    document_type: str = Query(..., description="Type of document being generated")
) -> Dict[str, Any]:
    """
    Deduct credits for document generation.
    For now, this is a no-op in development mode.
    """
    # In production, this would deduct from user's credit balance
    credit_costs = {
        "invoice": 1,
        "infographic": 2,
        "formal": 1,
    }

    cost = credit_costs.get(document_type, 1)

    logger.info(f"Deducting {cost} credits for {document_type} generation")

    return {
        "message": f"Credits deducted for {document_type}",
        "credits_deducted": cost,
        "new_balance": 999  # Mock balance for development
    }


@router.get("/packages")
async def get_credit_packages() -> Dict[str, Any]:
    """
    Get available credit packages for purchase.
    """
    return {
        "packages": [
            {
                "id": "basic",
                "name": "Basic",
                "credits": 10,
                "price": 9.99,
                "currency": "USD"
            },
            {
                "id": "standard",
                "name": "Standard",
                "credits": 50,
                "price": 39.99,
                "currency": "USD"
            },
            {
                "id": "premium",
                "name": "Premium",
                "credits": 100,
                "price": 69.99,
                "currency": "USD"
            }
        ]
    }


@router.post("/purchase")
async def purchase_credits(
    package_id: str,
    payment_method: str = "test"
) -> Dict[str, Any]:
    """
    Purchase credit package.
    For development, this instantly adds credits.
    """
    packages = {
        "basic": 10,
        "standard": 50,
        "premium": 100
    }

    if package_id not in packages:
        raise HTTPException(status_code=404, detail="Package not found")

    credits_added = packages[package_id]

    return {
        "success": True,
        "message": f"Successfully purchased {credits_added} credits",
        "credits_added": credits_added,
        "new_balance": 1000 + credits_added  # Mock calculation
    }