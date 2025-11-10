from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.schemas.credits import (
    CreditsPurchaseRequest,
    CreditsPurchaseResponse,
    CreditsBalanceResponse,
    CreditsPackage,
    CreditsPackagesResponse
)
from app.models.user import User
from app.utils.dependencies import get_current_active_user
from app.database import get_database

router = APIRouter()

# Credits package definitions
CREDITS_PACKAGES = {
    "small": {"name": "Small Package", "credits": 400, "price": 9.99},
    "medium": {"name": "Medium Package", "credits": 1000, "price": 19.99},
    "large": {"name": "Large Package", "credits": 10000, "price": 59.99}
}

# Document generation costs
DOCUMENT_COSTS = {
    "formal": 34,
    "infographic": 52
}


@router.get("/packages", response_model=CreditsPackagesResponse)
async def get_credits_packages():
    """
    Get available credits packages

    Returns:
        List of available credits packages
    """
    packages = [
        CreditsPackage(
            id=package_id,
            name=package_data["name"],
            credits=package_data["credits"],
            price=package_data["price"],
            currency="USD"
        )
        for package_id, package_data in CREDITS_PACKAGES.items()
    ]

    return CreditsPackagesResponse(packages=packages)


@router.get("/balance", response_model=CreditsBalanceResponse)
async def get_credits_balance(current_user: User = Depends(get_current_active_user)):
    """
    Get current user's credits balance

    Args:
        current_user: Current authenticated user

    Returns:
        User's current credits balance
    """
    return CreditsBalanceResponse(
        credits=current_user.credits,
        user_id=str(current_user.id)
    )


@router.post("/purchase", response_model=CreditsPurchaseResponse, status_code=status.HTTP_201_CREATED)
async def purchase_credits(
    purchase_data: CreditsPurchaseRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Purchase credits with Bitcoin

    Args:
        purchase_data: Purchase request data
        current_user: Current authenticated user

    Returns:
        Purchase confirmation with new balance

    Raises:
        HTTPException: If package is invalid or transaction fails
    """
    # Validate package
    if purchase_data.package not in CREDITS_PACKAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credits package"
        )

    package = CREDITS_PACKAGES[purchase_data.package]

    # In a real implementation, you would:
    # 1. Verify the Bitcoin transaction
    # 2. Check if transaction_id hasn't been used before
    # 3. Wait for blockchain confirmations
    # For now, we'll simulate a successful purchase

    db = get_database()

    # Check if transaction ID has been used before
    existing_transaction = await db.credit_transactions.find_one({
        "bitcoin_transaction_id": purchase_data.bitcoin_transaction_id
    })

    if existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This transaction ID has already been used"
        )

    # Add credits to user account
    new_credits = current_user.credits + package["credits"]

    await db.users.update_one(
        {"_id": current_user.id},
        {
            "$set": {
                "credits": new_credits,
                "updated_at": datetime.utcnow()
            }
        }
    )

    # Record the transaction
    transaction = {
        "user_id": current_user.id,
        "bitcoin_transaction_id": purchase_data.bitcoin_transaction_id,
        "package": purchase_data.package,
        "credits_added": package["credits"],
        "price": package["price"],
        "created_at": datetime.utcnow()
    }

    await db.credit_transactions.insert_one(transaction)

    return CreditsPurchaseResponse(
        message="Credits purchased successfully",
        credits_added=package["credits"],
        new_balance=new_credits,
        transaction_id=purchase_data.bitcoin_transaction_id
    )


@router.post("/deduct")
async def deduct_credits(
    document_type: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Deduct credits for document generation

    Args:
        document_type: Type of document (formal or infographic)
        current_user: Current authenticated user

    Returns:
        Success message with new balance

    Raises:
        HTTPException: If insufficient credits or invalid document type
    """
    if document_type not in DOCUMENT_COSTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Must be one of: {', '.join(DOCUMENT_COSTS.keys())}"
        )

    cost = DOCUMENT_COSTS[document_type]

    if current_user.credits < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Required: {cost}, Available: {current_user.credits}"
        )

    db = get_database()
    new_credits = current_user.credits - cost

    await db.users.update_one(
        {"_id": current_user.id},
        {
            "$set": {
                "credits": new_credits,
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {
        "message": "Credits deducted successfully",
        "credits_deducted": cost,
        "new_balance": new_credits
    }


@router.get("/cost/{document_type}")
async def get_document_cost(document_type: str):
    """
    Get the cost of generating a specific document type

    Args:
        document_type: Type of document (formal or infographic)

    Returns:
        Document generation cost in credits

    Raises:
        HTTPException: If document type is invalid
    """
    if document_type not in DOCUMENT_COSTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Must be one of: {', '.join(DOCUMENT_COSTS.keys())}"
        )

    return {
        "document_type": document_type,
        "cost": DOCUMENT_COSTS[document_type]
    }
