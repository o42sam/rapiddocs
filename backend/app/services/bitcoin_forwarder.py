"""
Bitcoin Fund Forwarding Service
Handles automatic forwarding of received Bitcoin payments to personal wallet.
"""

import logging
from typing import Dict, Optional
from bit import PrivateKeyTestnet, PrivateKey
from bit.network import NetworkAPI, satoshi_to_currency
from app.config import settings
from app.services.bitcoin_wallet import bitcoin_wallet_service

logger = logging.getLogger(__name__)


class BitcoinForwarderService:
    """Service for forwarding Bitcoin funds from payment addresses to personal wallet."""

    def __init__(self):
        self.personal_wallet = settings.BITCOIN_PERSONAL_WALLET
        self.is_testnet = settings.BITCOIN_NETWORK == "testnet"

    def forward_funds(self, private_key_wif: str, payment_address: str) -> Dict:
        """
        Forward all funds from a payment address to the personal wallet.

        Args:
            private_key_wif: WIF-encoded private key of the payment address
            payment_address: The payment address to forward from

        Returns:
            Dict containing:
            - success: Boolean indicating if forwarding succeeded
            - tx_hash: Transaction hash of the forwarding transaction
            - amount_forwarded: Amount forwarded in BTC
            - fee: Transaction fee in BTC
            - message: Status message
        """
        try:
            # Validate personal wallet is configured
            if not self.personal_wallet:
                logger.error("Personal wallet address not configured")
                return {
                    "success": False,
                    "tx_hash": None,
                    "amount_forwarded": 0,
                    "fee": 0,
                    "message": "Personal wallet not configured"
                }

            # Load the private key
            key = bitcoin_wallet_service.get_private_key_object(private_key_wif)

            # Verify the address matches
            if key.address != payment_address:
                logger.error(f"Private key does not match payment address {payment_address}")
                return {
                    "success": False,
                    "tx_hash": None,
                    "amount_forwarded": 0,
                    "fee": 0,
                    "message": "Private key mismatch"
                }

            # Get current balance
            balance_satoshis = key.get_balance()
            balance_btc = balance_satoshis / 100000000

            logger.info(f"Current balance of {payment_address}: {balance_btc} BTC")

            if balance_satoshis == 0:
                return {
                    "success": False,
                    "tx_hash": None,
                    "amount_forwarded": 0,
                    "fee": 0,
                    "message": "No funds to forward"
                }

            # Get unspent outputs
            key.get_unspents()

            # Estimate fee (using medium priority)
            # bit library will automatically calculate and deduct fee
            estimated_fee_satoshis = 2000  # Approximate fee in satoshis

            if balance_satoshis <= estimated_fee_satoshis:
                return {
                    "success": False,
                    "tx_hash": None,
                    "amount_forwarded": 0,
                    "fee": 0,
                    "message": "Balance too low to cover transaction fee"
                }

            # Calculate amount to send (balance - fee, bit will adjust automatically)
            # We use 'unspent' to send all available funds
            amount_to_send_satoshis = balance_satoshis - estimated_fee_satoshis

            logger.info(f"Forwarding {amount_to_send_satoshis / 100000000} BTC to {self.personal_wallet}")

            # Create and broadcast transaction
            # The fee parameter in bit is in satoshis per byte, using 'medium' for automatic fee estimation
            outputs = [(self.personal_wallet, amount_to_send_satoshis, 'satoshi')]

            tx_hash = key.send(outputs, fee=50, absolute_fee=False)  # 50 satoshis/byte

            amount_forwarded_btc = amount_to_send_satoshis / 100000000
            fee_btc = estimated_fee_satoshis / 100000000

            logger.info(f"Successfully forwarded {amount_forwarded_btc} BTC. TX: {tx_hash}")

            return {
                "success": True,
                "tx_hash": tx_hash,
                "amount_forwarded": amount_forwarded_btc,
                "fee": fee_btc,
                "message": "Funds forwarded successfully"
            }

        except ValueError as e:
            # Specific handling for insufficient funds
            logger.error(f"Insufficient funds error: {str(e)}")
            return {
                "success": False,
                "tx_hash": None,
                "amount_forwarded": 0,
                "fee": 0,
                "message": f"Insufficient funds: {str(e)}"
            }

        except Exception as e:
            logger.error(f"Error forwarding funds from {payment_address}: {str(e)}")
            return {
                "success": False,
                "tx_hash": None,
                "amount_forwarded": 0,
                "fee": 0,
                "message": f"Error forwarding funds: {str(e)}"
            }

    def get_recommended_fee(self) -> int:
        """
        Get recommended transaction fee in satoshis per byte.

        Returns:
            Recommended fee in satoshis/byte
        """
        try:
            # For testnet, use a fixed low fee
            if self.is_testnet:
                return 1  # 1 satoshi per byte for testnet

            # For mainnet, you could integrate with a fee estimation API
            # For now, using a moderate fixed fee
            return 50  # 50 satoshis per byte

        except Exception as e:
            logger.error(f"Error getting recommended fee: {str(e)}")
            return 50  # Default to 50 sat/byte


# Initialize singleton instance
bitcoin_forwarder_service = BitcoinForwarderService()
