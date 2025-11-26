"""
Paystack payment routes for card and bank transfer payments
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from typing import Optional, List
from datetime import datetime, timedelta
from bson import ObjectId

from app.database import get_database
from app.models.user import User
from app.models.paystack_transaction import (
    PaystackTransaction,
    PaystackVirtualAccount,
    PaystackWebhookLog
)
from app.schemas.paystack import (
    InitializeCardPaymentRequest,
    InitializeCardPaymentResponse,
    InitializeVirtualAccountRequest,
    VirtualAccountResponse,
    VerifyPaymentRequest,
    PaymentVerificationResponse,
    TransactionResponse
)
from app.schemas.credits import CreditsPackage
from app.services.paystack import paystack_service
from app.utils.dependencies import get_current_active_user
from app.utils.logger import get_logger
from app.utils.exceptions import PaymentError

logger = get_logger('paystack_route')
router = APIRouter()


@router.post("/paystack/initialize-card", response_model=InitializeCardPaymentResponse)
async def initialize_card_payment(
    request: InitializeCardPaymentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Initialize a card payment with Paystack

    This creates a transaction and returns an authorization URL
    where the user can complete their payment.
    """
    logger.info(f"Initializing card payment for user: {current_user.id}")

    db = get_database()

    try:
        # Fetch credits package to get price
        package = await db.credits_packages.find_one({"_id": ObjectId(request.credits_package_id)})
        if not package:
            raise HTTPException(status_code=404, detail="Credits package not found")

        # Use the amount from the package
        amount = package["price"]
        credits = package["credits"]

        # Generate unique reference
        reference = paystack_service.generate_reference("paystack_card")

        # Create transaction record
        transaction = PaystackTransaction(
            user_id=str(current_user.id),
            reference=reference,
            payment_method="card",
            amount=paystack_service.naira_to_kobo(amount),
            currency=paystack_service.currency,
            credits_package_id=request.credits_package_id,
            credits_amount=credits,
            status="pending",
            metadata={
                "user_email": current_user.email,
                "user_name": current_user.full_name,
                "package_name": package.get("name", "Credits Package")
            }
        )

        # Initialize payment with Paystack
        paystack_response = paystack_service.initialize_transaction(
            email=request.email or current_user.email,
            amount=amount,
            reference=reference,
            callback_url=request.callback_url,
            metadata={
                "user_id": str(current_user.id),
                "credits_package_id": request.credits_package_id,
                "credits_amount": credits
            }
        )

        # Update transaction with Paystack response
        transaction.authorization_url = paystack_response["authorization_url"]
        transaction.access_code = paystack_response["access_code"]
        transaction.paystack_reference = paystack_response["reference"]

        # Save to database
        await db.paystack_transactions.insert_one(transaction.dict(by_alias=True, exclude={"id"}))

        logger.info(f"Card payment initialized: {reference}")

        return InitializeCardPaymentResponse(
            status="success",
            message="Payment initialized successfully",
            reference=reference,
            authorization_url=transaction.authorization_url,
            access_code=transaction.access_code
        )

    except PaymentError as e:
        logger.error(f"Payment initialization failed: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error during payment initialization: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize payment")


@router.post("/paystack/initialize-transfer", response_model=VirtualAccountResponse)
async def initialize_bank_transfer(
    request: InitializeVirtualAccountRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a dedicated virtual account for bank transfer payment

    This generates a unique bank account number that the user can
    transfer money to. Payment is automatically confirmed when funds arrive.
    """
    logger.info(f"Initializing bank transfer for user: {current_user.id}")

    db = get_database()

    try:
        # Fetch credits package
        package = await db.credits_packages.find_one({"_id": ObjectId(request.credits_package_id)})
        if not package:
            raise HTTPException(status_code=404, detail="Credits package not found")

        amount = package["price"]
        credits = package["credits"]

        # Generate unique reference
        reference = paystack_service.generate_reference("paystack_transfer")

        # Check if user already has an active virtual account for this amount
        existing_account = await db.paystack_virtual_accounts.find_one({
            "user_id": str(current_user.id),
            "active": True
        })

        if existing_account:
            # Reuse existing virtual account
            logger.info(f"Reusing existing virtual account for user: {current_user.id}")
            account_data = existing_account
        else:
            # Create new dedicated virtual account
            virtual_account_response = paystack_service.create_dedicated_virtual_account(
                email=request.email or current_user.email,
                first_name=request.first_name,
                last_name=request.last_name,
                phone=request.phone,
                preferred_bank=request.preferred_bank,
                metadata={
                    "user_id": str(current_user.id),
                    "reference": reference
                }
            )

            # Save virtual account to database
            virtual_account = PaystackVirtualAccount(
                user_id=str(current_user.id),
                paystack_id=str(virtual_account_response["id"]),
                account_number=virtual_account_response["account_number"],
                bank_name=virtual_account_response["bank_name"],
                bank_slug=virtual_account_response["bank_slug"],
                account_name=virtual_account_response["account_name"],
                metadata={
                    "email": request.email or current_user.email,
                    "first_name": request.first_name,
                    "last_name": request.last_name
                }
            )

            await db.paystack_virtual_accounts.insert_one(
                virtual_account.dict(by_alias=True, exclude={"id"})
            )

            account_data = virtual_account.dict()

        # Create transaction record
        transaction = PaystackTransaction(
            user_id=str(current_user.id),
            reference=reference,
            payment_method="bank_transfer",
            amount=paystack_service.naira_to_kobo(amount),
            currency=paystack_service.currency,
            credits_package_id=request.credits_package_id,
            credits_amount=credits,
            status="pending",
            virtual_account_id=account_data.get("paystack_id") or str(account_data.get("_id")),
            account_number=account_data.get("account_number"),
            bank_name=account_data.get("bank_name"),
            account_name=account_data.get("account_name"),
            expires_at=datetime.utcnow() + timedelta(hours=24),  # 24 hour expiry
            metadata={
                "user_email": current_user.email,
                "user_name": current_user.full_name,
                "package_name": package.get("name", "Credits Package")
            }
        )

        await db.paystack_transactions.insert_one(transaction.dict(by_alias=True, exclude={"id"}))

        logger.info(f"Bank transfer initialized: {reference}")

        return VirtualAccountResponse(
            status="success",
            message="Virtual account created successfully",
            reference=reference,
            account_number=transaction.account_number,
            bank_name=transaction.bank_name,
            account_name=transaction.account_name,
            amount=amount,
            expires_at=transaction.expires_at.isoformat() if transaction.expires_at else None
        )

    except PaymentError as e:
        logger.error(f"Virtual account creation failed: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error creating virtual account: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create virtual account")


@router.post("/paystack/verify", response_model=PaymentVerificationResponse)
async def verify_payment(
    request: VerifyPaymentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Verify a payment and add credits to user account

    This endpoint should be called after payment is completed
    to verify the transaction and credit the user's account.
    """
    logger.info(f"Verifying payment: {request.reference}")

    db = get_database()

    try:
        # Find transaction in database
        transaction = await db.paystack_transactions.find_one({
            "reference": request.reference,
            "user_id": str(current_user.id)
        })

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # If already successful, return cached result
        if transaction["status"] == "success":
            logger.info(f"Payment already verified: {request.reference}")
            return PaymentVerificationResponse(
                status="success",
                message="Payment already verified",
                reference=request.reference,
                amount=paystack_service.kobo_to_naira(transaction["amount"]),
                credits_added=transaction["credits_amount"],
                payment_status="success",
                paid_at=transaction.get("paid_at").isoformat() if transaction.get("paid_at") else None
            )

        # Verify with Paystack
        verification = paystack_service.verify_transaction(request.reference)

        # Update transaction status
        update_data = {
            "status": verification["status"],
            "gateway_response": verification.get("gateway_response"),
            "updated_at": datetime.utcnow()
        }

        if verification["status"] == "success":
            update_data["paid_at"] = datetime.utcnow()

            # Add credits to user account
            await db.users.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$inc": {"credits": transaction["credits_amount"]}}
            )

            logger.info(f"Added {transaction['credits_amount']} credits to user {current_user.id}")

        await db.paystack_transactions.update_one(
            {"reference": request.reference},
            {"$set": update_data}
        )

        return PaymentVerificationResponse(
            status="success" if verification["status"] == "success" else "failed",
            message="Payment verified successfully" if verification["status"] == "success" else "Payment verification failed",
            reference=request.reference,
            amount=verification["amount"],
            credits_added=transaction["credits_amount"] if verification["status"] == "success" else 0,
            payment_status=verification["status"],
            paid_at=verification.get("paid_at")
        )

    except PaymentError as e:
        logger.error(f"Payment verification failed: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error during verification: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify payment")


@router.get("/paystack/transactions", response_model=List[TransactionResponse])
async def get_user_transactions(
    current_user: User = Depends(get_current_active_user),
    limit: int = 20,
    status: Optional[str] = None
):
    """Get user's payment transaction history"""
    logger.info(f"Fetching transactions for user: {current_user.id}")

    db = get_database()

    query = {"user_id": str(current_user.id)}
    if status:
        query["status"] = status

    transactions = await db.paystack_transactions.find(query).sort("created_at", -1).limit(limit).to_list(limit)

    return [
        TransactionResponse(
            id=str(txn["_id"]),
            reference=txn["reference"],
            amount=paystack_service.kobo_to_naira(txn["amount"]),
            currency=txn["currency"],
            status=txn["status"],
            payment_method=txn["payment_method"],
            credits_amount=txn["credits_amount"],
            created_at=txn["created_at"].isoformat(),
            paid_at=txn.get("paid_at").isoformat() if txn.get("paid_at") else None
        )
        for txn in transactions
    ]


@router.get("/paystack/config")
async def get_paystack_config():
    """Get Paystack public configuration for frontend"""
    return {
        "public_key": paystack_service.public_key,
        "currency": paystack_service.currency
    }


@router.post("/paystack/webhook")
async def paystack_webhook(
    request: Request,
    x_paystack_signature: Optional[str] = Header(None)
):
    """
    Handle Paystack webhook events

    Paystack sends webhooks for various events like:
    - charge.success: Card payment successful
    - transfer.success: Bank transfer received
    - transfer.failed: Bank transfer failed
    """
    logger.info("Received Paystack webhook")

    db = get_database()

    try:
        # Get raw body for signature verification
        body = await request.body()

        # Verify webhook signature
        if not x_paystack_signature:
            logger.warning("Webhook received without signature")
            raise HTTPException(status_code=400, detail="Missing signature")

        is_valid = paystack_service.verify_webhook_signature(body, x_paystack_signature)

        # Parse event data
        import json
        event_data = json.loads(body.decode('utf-8'))

        event_type = event_data.get("event")
        data = event_data.get("data", {})

        # Log webhook event
        webhook_log = PaystackWebhookLog(
            event_type=event_type,
            event_data=event_data,
            signature=x_paystack_signature,
            verified=is_valid
        )

        await db.paystack_webhook_logs.insert_one(webhook_log.dict(by_alias=True, exclude={"id"}))

        if not is_valid:
            logger.warning("Invalid webhook signature")
            return {"status": "error", "message": "Invalid signature"}

        # Process different event types
        reference = data.get("reference")

        if event_type == "charge.success":
            # Card payment successful
            logger.info(f"Processing charge.success for reference: {reference}")

            transaction = await db.paystack_transactions.find_one({"paystack_reference": reference})

            if transaction and transaction["status"] != "success":
                # Update transaction
                await db.paystack_transactions.update_one(
                    {"_id": transaction["_id"]},
                    {
                        "$set": {
                            "status": "success",
                            "paid_at": datetime.utcnow(),
                            "gateway_response": data.get("gateway_response"),
                            "webhook_received": True,
                            "webhook_verified": True,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )

                # Add credits to user
                await db.users.update_one(
                    {"_id": ObjectId(transaction["user_id"])},
                    {"$inc": {"credits": transaction["credits_amount"]}}
                )

                logger.info(f"Credits added for card payment: {reference}")

        elif event_type == "transfer.success" or event_type == "charge.success":
            # Bank transfer received (or any successful charge)
            logger.info(f"Processing transfer/charge success for reference: {reference}")

            # Find transaction by reference or virtual account
            transaction = await db.paystack_transactions.find_one({
                "$or": [
                    {"reference": reference},
                    {"paystack_reference": reference},
                    {"account_number": data.get("recipient", {}).get("details", {}).get("account_number")}
                ],
                "status": "pending"
            })

            if transaction:
                # Update transaction
                await db.paystack_transactions.update_one(
                    {"_id": transaction["_id"]},
                    {
                        "$set": {
                            "status": "success",
                            "paid_at": datetime.utcnow(),
                            "paystack_reference": reference,
                            "webhook_received": True,
                            "webhook_verified": True,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )

                # Add credits to user
                await db.users.update_one(
                    {"_id": ObjectId(transaction["user_id"])},
                    {"$inc": {"credits": transaction["credits_amount"]}}
                )

                logger.info(f"Credits added for bank transfer: {reference}")

        elif event_type in ["transfer.failed", "transfer.reversed"]:
            # Payment failed
            logger.info(f"Processing payment failure for reference: {reference}")

            await db.paystack_transactions.update_one(
                {"$or": [{"reference": reference}, {"paystack_reference": reference}]},
                {
                    "$set": {
                        "status": "failed",
                        "error_message": data.get("message", "Payment failed"),
                        "webhook_received": True,
                        "webhook_verified": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

        # Update webhook log as processed
        await db.paystack_webhook_logs.update_one(
            {"_id": webhook_log.id},
            {
                "$set": {
                    "processed": True,
                    "processed_at": datetime.utcnow(),
                    "transaction_reference": reference
                }
            }
        )

        logger.info(f"Webhook processed successfully: {event_type}")
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")

        # Log error
        if 'webhook_log' in locals():
            await db.paystack_webhook_logs.update_one(
                {"_id": webhook_log.id},
                {
                    "$set": {
                        "processing_error": str(e),
                        "processed_at": datetime.utcnow()
                    }
                }
            )

        return {"status": "error", "message": str(e)}
