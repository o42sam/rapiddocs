"""
Bitcoin Payment Background Processor
Automatically processes confirmed Bitcoin payments without user intervention.
"""

import logging
import asyncio
from datetime import datetime
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.database import get_database
from app.services.bitcoin_monitor import bitcoin_monitor_service
from app.services.bitcoin_forwarder import bitcoin_forwarder_service
from app.config import settings

logger = logging.getLogger(__name__)


class BitcoinPaymentProcessor:
    """Background processor for automatic Bitcoin payment handling."""

    def __init__(self):
        self.is_running = False
        self.check_interval = 30  # Check every 30 seconds

    async def process_pending_payments(self):
        """
        Check all pending/confirming payments and process confirmed ones automatically.
        This should run in the background continuously.
        """
        try:
            db = get_database()

            # Find all payments that are pending or confirming
            cursor = db.bitcoin_payments.find({
                "status": {"$in": ["pending", "confirming"]}
            })

            payments = await cursor.to_list(length=None)

            for payment in payments:
                try:
                    # Check if payment has expired
                    if datetime.utcnow() > payment["expires_at"]:
                        await db.bitcoin_payments.update_one(
                            {"_id": payment["_id"]},
                            {"$set": {"status": "expired"}}
                        )
                        logger.info(f"Payment {payment['_id']} expired")
                        continue

                    # Check blockchain for payment status
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

                    # If payment is confirmed, process it automatically
                    if payment_check["status"] == "confirmed":
                        logger.info(f"Payment {payment['_id']} confirmed! Auto-processing...")

                        # Add credits to user account
                        await db.users.update_one(
                            {"_id": ObjectId(payment["user_id"])},
                            {"$inc": {"credits": payment["credits"]}}
                        )

                        # Decrypt private key and forward funds
                        from app.routes.bitcoin import decrypt_private_key
                        decrypted_private_key = decrypt_private_key(payment["private_key_encrypted"])
                        forwarding_result = bitcoin_forwarder_service.forward_funds(
                            decrypted_private_key,
                            payment["payment_address"]
                        )

                        # Update payment status
                        update_data["status"] = "forwarded" if forwarding_result["success"] else "confirmed"
                        update_data["confirmed_at"] = datetime.utcnow()
                        update_data["completed_at"] = datetime.utcnow()

                        if forwarding_result["success"]:
                            update_data["forwarding_tx_hash"] = forwarding_result["tx_hash"]
                            update_data["forwarding_completed_at"] = datetime.utcnow()
                        else:
                            logger.warning(f"Failed to forward funds for payment {payment['_id']}: {forwarding_result['message']}")

                        logger.info(f"Auto-processed payment {payment['_id']}: Added {payment['credits']} credits to user {payment['user_id']}")

                    elif payment_check["confirmations"] > 0:
                        update_data["status"] = "confirming"

                    # Update database
                    await db.bitcoin_payments.update_one(
                        {"_id": payment["_id"]},
                        {"$set": update_data}
                    )

                except Exception as e:
                    logger.error(f"Error processing payment {payment['_id']}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error in process_pending_payments: {str(e)}")

    async def start_background_processor(self):
        """
        Start the background payment processor.
        This runs continuously and checks for confirmed payments.
        """
        self.is_running = True
        logger.info("Bitcoin payment background processor started")

        while self.is_running:
            try:
                await self.process_pending_payments()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in background processor loop: {str(e)}")
                await asyncio.sleep(self.check_interval)

    def stop_background_processor(self):
        """Stop the background processor."""
        self.is_running = False
        logger.info("Bitcoin payment background processor stopped")


# Singleton instance
bitcoin_payment_processor = BitcoinPaymentProcessor()
