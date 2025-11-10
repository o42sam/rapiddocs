"""
Bitcoin Payment Monitoring Service
Monitors Bitcoin blockchain for incoming payments and tracks confirmations.
"""

import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


class BitcoinMonitorService:
    """Service for monitoring Bitcoin payments on the blockchain."""

    def __init__(self):
        self.api_url = settings.BITCOIN_API_URL
        self.required_confirmations = settings.BITCOIN_CONFIRMATIONS_REQUIRED

    def check_payment(self, address: str, expected_amount_btc: float) -> Dict:
        """
        Check if a payment has been received at the given address.

        Args:
            address: The Bitcoin address to monitor
            expected_amount_btc: The expected payment amount in BTC

        Returns:
            Dict containing:
            - paid: Boolean indicating if payment is confirmed
            - amount_received: Amount received in BTC
            - confirmations: Number of confirmations
            - tx_hash: Transaction hash (if found)
            - status: Status message
        """
        try:
            # Get address information from blockchain API
            response = requests.get(f"{self.api_url}/address/{address}", timeout=30)

            if response.status_code != 200:
                logger.error(f"Failed to fetch address data: {response.status_code}")
                return {
                    "paid": False,
                    "amount_received": 0,
                    "confirmations": 0,
                    "tx_hash": None,
                    "status": "error_fetching_data"
                }

            address_data = response.json()

            # Get transactions for this address
            chain_stats = address_data.get("chain_stats", {})
            funded_txo_sum = chain_stats.get("funded_txo_sum", 0)  # Total received in satoshis
            spent_txo_sum = chain_stats.get("spent_txo_sum", 0)  # Total spent in satoshis

            # Calculate balance
            balance_satoshis = funded_txo_sum - spent_txo_sum
            balance_btc = balance_satoshis / 100000000

            logger.info(f"Address {address} balance: {balance_btc} BTC (expected: {expected_amount_btc} BTC)")

            # Check if payment amount is sufficient
            if balance_btc < expected_amount_btc:
                return {
                    "paid": False,
                    "amount_received": balance_btc,
                    "confirmations": 0,
                    "tx_hash": None,
                    "status": "insufficient_amount"
                }

            # Get transaction details to check confirmations
            tx_response = requests.get(f"{self.api_url}/address/{address}/txs", timeout=30)

            if tx_response.status_code != 200:
                logger.error(f"Failed to fetch transactions: {tx_response.status_code}")
                return {
                    "paid": False,
                    "amount_received": balance_btc,
                    "confirmations": 0,
                    "tx_hash": None,
                    "status": "error_fetching_transactions"
                }

            transactions = tx_response.json()

            # Find the transaction that funded this address
            funding_tx = None
            max_confirmations = 0

            for tx in transactions:
                # Check if this transaction has outputs to our address
                for vout in tx.get("vout", []):
                    if vout.get("scriptpubkey_address") == address:
                        # Get confirmation count
                        if tx.get("status", {}).get("confirmed"):
                            block_height = tx["status"].get("block_height", 0)
                            # Get current block height
                            latest_block_response = requests.get(f"{self.api_url}/blocks/tip/height", timeout=30)
                            if latest_block_response.status_code == 200:
                                current_height = int(latest_block_response.text)
                                confirmations = current_height - block_height + 1

                                if confirmations > max_confirmations:
                                    max_confirmations = confirmations
                                    funding_tx = tx

            if funding_tx:
                tx_hash = funding_tx["txid"]
                logger.info(f"Found funding transaction {tx_hash} with {max_confirmations} confirmations")

                if max_confirmations >= self.required_confirmations:
                    return {
                        "paid": True,
                        "amount_received": balance_btc,
                        "confirmations": max_confirmations,
                        "tx_hash": tx_hash,
                        "status": "confirmed"
                    }
                else:
                    return {
                        "paid": False,
                        "amount_received": balance_btc,
                        "confirmations": max_confirmations,
                        "tx_hash": tx_hash,
                        "status": "pending_confirmations"
                    }

            return {
                "paid": False,
                "amount_received": balance_btc,
                "confirmations": 0,
                "tx_hash": None,
                "status": "no_transaction_found"
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error checking payment for {address}: {str(e)}")
            return {
                "paid": False,
                "amount_received": 0,
                "confirmations": 0,
                "tx_hash": None,
                "status": "network_error"
            }
        except Exception as e:
            logger.error(f"Error checking payment for {address}: {str(e)}")
            return {
                "paid": False,
                "amount_received": 0,
                "confirmations": 0,
                "tx_hash": None,
                "status": "error"
            }

    def get_btc_to_usd_rate(self) -> Optional[float]:
        """
        Get current BTC to USD exchange rate.

        Returns:
            Exchange rate as float, or None if unable to fetch
        """
        try:
            # Using CoinGecko API (no key required)
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                rate = data.get("bitcoin", {}).get("usd")
                if rate:
                    logger.info(f"Current BTC/USD rate: ${rate}")
                    return float(rate)

            logger.warning("Failed to fetch BTC/USD rate")
            return None

        except Exception as e:
            logger.error(f"Error fetching BTC/USD rate: {str(e)}")
            return None

    def calculate_btc_amount(self, usd_amount: float) -> Optional[float]:
        """
        Calculate BTC amount from USD amount based on current exchange rate.

        Args:
            usd_amount: Amount in USD

        Returns:
            Amount in BTC, or None if unable to calculate
        """
        rate = self.get_btc_to_usd_rate()
        if rate:
            btc_amount = usd_amount / rate
            logger.info(f"${usd_amount} USD = {btc_amount} BTC")
            return btc_amount
        return None


# Initialize singleton instance
bitcoin_monitor_service = BitcoinMonitorService()
