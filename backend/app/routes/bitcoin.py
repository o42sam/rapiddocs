"""
Bitcoin Payment Routes
API endpoints for Bitcoin payment integration.
"""

import logging
import base64
import io
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from cryptography.fernet import Fernet
import qrcode

from app.database import get_database
from app.models.user import User
from app.models.bitcoin_payment import BitcoinPayment, BitcoinPaymentStatus
from app.schemas.bitcoin import (
    BitcoinPaymentInitRequest,
    BitcoinPaymentInitResponse,
    BitcoinPaymentStatusRequest,
    BitcoinPaymentStatusResponse,
    BitcoinPaymentConfirmResponse
)
from app.services.bitcoin_wallet import bitcoin_wallet_service
from app.services.bitcoin_monitor import bitcoin_monitor_service
from app.services.bitcoin_forwarder import bitcoin_forwarder_service
from app.routes.auth import get_current_user
from app.config import settings
from bson import ObjectId

logger = logging.getLogger(__name__)
router = APIRouter()

# Credits packages
CREDITS_PACKAGES = {
    "small": {"credits": 400, "price": 9.99},
    "medium": {"credits": 1000, "price": 19.99},
    "large": {"credits": 10000, "price": 59.99}
}

# Encryption key for storing private keys (in production, use a proper key management system)
# Generate this once and store securely: Fernet.generate_key()
ENCRYPTION_KEY = settings.JWT_SECRET_KEY.encode()[:32]  # Using first 32 bytes of JWT secret
cipher = Fernet(base64.urlsafe_b64encode(ENCRYPTION_KEY))


def encrypt_private_key(private_key: str) -> str:
    """Encrypt a private key for secure storage."""
    return cipher.encrypt(private_key.encode()).decode()


def decrypt_private_key(encrypted_key: str) -> str:
    """Decrypt a private key."""
    return cipher.decrypt(encrypted_key.encode()).decode()


@router.post("/initiate", response_model=BitcoinPaymentInitResponse)
async def initiate_bitcoin_payment(
    request: BitcoinPaymentInitRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Initiate a Bitcoin payment for credits purchase.
    Generates a unique Bitcoin address and QR code for payment.
    """
    try:
        db = get_database()

        # Validate package
        if request.package not in CREDITS_PACKAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid package selected"
            )

        package_info = CREDITS_PACKAGES[request.package]
        amount_usd = package_info["price"]
        credits = package_info["credits"]

        # Get BTC amount based on current exchange rate
        amount_btc = bitcoin_monitor_service.calculate_btc_amount(amount_usd)
        if not amount_btc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to calculate BTC amount. Please try again."
            )

        btc_usd_rate = bitcoin_monitor_service.get_btc_to_usd_rate()

        # Generate a new Bitcoin address for this payment
        wallet_data = bitcoin_wallet_service.generate_payment_address()
        payment_address = wallet_data["address"]
        private_key = wallet_data["private_key"]

        # Encrypt the private key for secure storage
        encrypted_private_key = encrypt_private_key(private_key)

        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(minutes=settings.BITCOIN_PAYMENT_TIMEOUT_MINUTES)

        # Create payment record in database
        payment = BitcoinPayment(
            user_id=str(current_user.id),
            package=request.package,
            amount_usd=amount_usd,
            amount_btc=amount_btc,
            credits=credits,
            payment_address=payment_address,
            private_key_encrypted=encrypted_private_key,
            status="pending",
            expires_at=expires_at,
            btc_usd_rate=btc_usd_rate or 0,
            network=settings.BITCOIN_NETWORK
        )

        result = await db.bitcoin_payments.insert_one(payment.model_dump(by_alias=True, exclude={"id"}))
        payment_id = str(result.inserted_id)

        # Generate QR code for the Bitcoin address with amount
        bitcoin_uri = f"bitcoin:{payment_address}?amount={amount_btc}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(bitcoin_uri)
        qr.make(fit=True)

        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        logger.info(f"Created Bitcoin payment {payment_id} for user {current_user.id}: {amount_btc} BTC ({amount_usd} USD)")

        return BitcoinPaymentInitResponse(
            payment_id=payment_id,
            payment_address=payment_address,
            amount_btc=amount_btc,
            amount_usd=amount_usd,
            qr_code_data=qr_code_base64,
            expires_at=expires_at,
            message=f"Please send exactly {amount_btc} BTC to the provided address"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating Bitcoin payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate payment. Please try again."
        )


@router.post("/status", response_model=BitcoinPaymentStatusResponse)
async def check_bitcoin_payment_status(
    request: BitcoinPaymentStatusRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Check the status of a Bitcoin payment.
    Monitors the blockchain for payment confirmation.
    """
    try:
        db = get_database()

        # Get payment from database
        payment = await db.bitcoin_payments.find_one({"_id": ObjectId(request.payment_id)})

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        # Verify payment belongs to current user
        if payment["user_id"] != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to payment"
            )

        # Check if payment has expired
        if datetime.utcnow() > payment["expires_at"] and payment["status"] == "pending":
            await db.bitcoin_payments.update_one(
                {"_id": ObjectId(request.payment_id)},
                {"$set": {"status": "expired"}}
            )
            payment["status"] = "expired"

        # If payment is still pending or confirming, check blockchain
        if payment["status"] in ["pending", "confirming"]:
            payment_check = bitcoin_monitor_service.check_payment(
                payment["payment_address"],
                payment["amount_btc"]
            )

            # Update payment record
            update_data = {
                "confirmations": payment_check["confirmations"],
                "amount_received_btc": payment_check["amount_received"]
            }

            if payment_check["tx_hash"]:
                update_data["tx_hash"] = payment_check["tx_hash"]

            if payment_check["status"] == "confirmed":
                update_data["status"] = "confirmed"
                update_data["confirmed_at"] = datetime.utcnow()
            elif payment_check["confirmations"] > 0:
                update_data["status"] = "confirming"

            await db.bitcoin_payments.update_one(
                {"_id": ObjectId(request.payment_id)},
                {"$set": update_data}
            )

            payment.update(update_data)

        # Determine message based on status
        status_messages = {
            "pending": "Waiting for payment. Please send Bitcoin to the provided address.",
            "confirming": f"Payment received! Waiting for {settings.BITCOIN_CONFIRMATIONS_REQUIRED} confirmations ({payment['confirmations']}/{settings.BITCOIN_CONFIRMATIONS_REQUIRED}).",
            "confirmed": "Payment confirmed! Processing your credits...",
            "forwarded": "Payment processed successfully. Credits have been added to your account.",
            "failed": f"Payment failed: {payment.get('error_message', 'Unknown error')}",
            "expired": "Payment request has expired. Please create a new payment."
        }

        return BitcoinPaymentStatusResponse(
            payment_id=request.payment_id,
            status=payment["status"],
            payment_address=payment["payment_address"],
            amount_btc=payment["amount_btc"],
            amount_received_btc=payment["amount_received_btc"],
            amount_usd=payment["amount_usd"],
            confirmations=payment["confirmations"],
            required_confirmations=settings.BITCOIN_CONFIRMATIONS_REQUIRED,
            tx_hash=payment.get("tx_hash"),
            forwarding_tx_hash=payment.get("forwarding_tx_hash"),
            expires_at=payment["expires_at"],
            credits=payment["credits"],
            message=status_messages.get(payment["status"], "Processing payment...")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check payment status"
        )


@router.post("/confirm/{payment_id}", response_model=BitcoinPaymentConfirmResponse)
async def confirm_and_process_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Confirm a Bitcoin payment and process it (add credits, forward funds).
    This should be called after the payment status shows as 'confirmed'.
    """
    try:
        db = get_database()

        # Get payment from database
        payment = await db.bitcoin_payments.find_one({"_id": ObjectId(payment_id)})

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        # Verify payment belongs to current user
        if payment["user_id"] != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to payment"
            )

        # Check if payment is already processed
        if payment["status"] in ["forwarded"]:
            # Already processed, return success (idempotent)
            return BitcoinPaymentConfirmResponse(
                success=True,
                payment_id=payment_id,
                credits_added=payment["credits"],
                new_balance=current_user.credits,
                tx_hash=payment.get("tx_hash", ""),
                message="Payment already processed successfully"
            )

        # Check if payment is confirmed
        if payment["status"] != "confirmed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment is not confirmed. Current status: {payment['status']}"
            )

        # Add credits to user account (use $inc to avoid race conditions)
        result = await db.users.update_one(
            {"_id": current_user.id},
            {"$inc": {"credits": payment["credits"]}}
        )

        # Get updated credits
        updated_user = await db.users.find_one({"_id": current_user.id})
        new_credits = updated_user["credits"]

        # Forward funds to personal wallet
        decrypted_private_key = decrypt_private_key(payment["private_key_encrypted"])
        forwarding_result = bitcoin_forwarder_service.forward_funds(
            decrypted_private_key,
            payment["payment_address"]
        )

        # Update payment record
        update_data = {
            "status": "forwarded" if forwarding_result["success"] else "confirmed",
            "completed_at": datetime.utcnow()
        }

        if forwarding_result["success"]:
            update_data["forwarding_tx_hash"] = forwarding_result["tx_hash"]
            update_data["forwarding_completed_at"] = datetime.utcnow()
        else:
            logger.warning(f"Failed to forward funds for payment {payment_id}: {forwarding_result['message']}")

        await db.bitcoin_payments.update_one(
            {"_id": ObjectId(payment_id)},
            {"$set": update_data}
        )

        logger.info(f"Processed Bitcoin payment {payment_id} for user {current_user.id}: Added {payment['credits']} credits")

        return BitcoinPaymentConfirmResponse(
            success=True,
            payment_id=payment_id,
            credits_added=payment["credits"],
            new_balance=new_credits,
            tx_hash=payment["tx_hash"],
            message=f"Successfully added {payment['credits']} credits to your account"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing payment {payment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment"
        )
