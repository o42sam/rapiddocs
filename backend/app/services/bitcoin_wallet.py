"""
Bitcoin Wallet Service
Handles wallet generation, address creation, and private key management for Bitcoin payments.
"""

import logging
from typing import Dict, Optional
from bit import PrivateKeyTestnet, PrivateKey
from bit.network import NetworkAPI
from app.config import settings

logger = logging.getLogger(__name__)


class BitcoinWalletService:
    """Service for managing Bitcoin wallets and addresses."""

    def __init__(self):
        self.network = settings.BITCOIN_NETWORK
        self.is_testnet = self.network == "testnet"

    def generate_payment_address(self) -> Dict[str, str]:
        """
        Generate a new Bitcoin address for receiving payment.

        Returns:
            Dict containing:
            - address: The Bitcoin address
            - private_key: The WIF-encoded private key (must be stored securely)
            - network: The network (mainnet/testnet)
        """
        try:
            # Generate new private key based on network
            if self.is_testnet:
                key = PrivateKeyTestnet()
            else:
                key = PrivateKey()

            address = key.address
            private_key_wif = key.to_wif()

            logger.info(f"Generated new Bitcoin address: {address} on {self.network}")

            return {
                "address": address,
                "private_key": private_key_wif,
                "network": self.network
            }

        except Exception as e:
            logger.error(f"Error generating Bitcoin address: {str(e)}")
            raise Exception(f"Failed to generate Bitcoin address: {str(e)}")

    def get_address_balance(self, address: str) -> float:
        """
        Get the balance of a Bitcoin address in BTC.

        Args:
            address: The Bitcoin address to check

        Returns:
            Balance in BTC
        """
        try:
            if self.is_testnet:
                balance_satoshis = NetworkAPI.get_balance_testnet(address)
            else:
                balance_satoshis = NetworkAPI.get_balance(address)

            # Convert satoshis to BTC
            balance_btc = balance_satoshis / 100000000

            logger.info(f"Balance for address {address}: {balance_btc} BTC")
            return balance_btc

        except Exception as e:
            logger.error(f"Error getting balance for {address}: {str(e)}")
            raise Exception(f"Failed to get balance: {str(e)}")

    def get_private_key_object(self, private_key_wif: str):
        """
        Get a PrivateKey object from WIF-encoded private key.

        Args:
            private_key_wif: WIF-encoded private key

        Returns:
            PrivateKey or PrivateKeyTestnet object
        """
        try:
            if self.is_testnet:
                return PrivateKeyTestnet(private_key_wif)
            else:
                return PrivateKey(private_key_wif)
        except Exception as e:
            logger.error(f"Error loading private key: {str(e)}")
            raise Exception(f"Failed to load private key: {str(e)}")

    def get_transactions(self, address: str) -> list:
        """
        Get transaction history for an address.

        Args:
            address: The Bitcoin address

        Returns:
            List of transactions
        """
        try:
            if self.is_testnet:
                transactions = NetworkAPI.get_transactions_testnet(address)
            else:
                transactions = NetworkAPI.get_transactions(address)

            logger.info(f"Retrieved {len(transactions)} transactions for {address}")
            return transactions

        except Exception as e:
            logger.error(f"Error getting transactions for {address}: {str(e)}")
            raise Exception(f"Failed to get transactions: {str(e)}")

    def validate_address(self, address: str) -> bool:
        """
        Validate if a Bitcoin address is properly formatted.

        Args:
            address: The Bitcoin address to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation - check prefix and length
            if self.is_testnet:
                # Testnet addresses start with 'm', 'n', or '2' (for P2SH)
                if not (address.startswith('m') or address.startswith('n') or address.startswith('2')):
                    return False
            else:
                # Mainnet addresses start with '1' or '3' (for P2SH) or 'bc1' (for bech32)
                if not (address.startswith('1') or address.startswith('3') or address.startswith('bc1')):
                    return False

            # Check length (typical Bitcoin addresses are 26-35 characters)
            if len(address) < 26 or len(address) > 35:
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating address {address}: {str(e)}")
            return False


# Initialize singleton instance
bitcoin_wallet_service = BitcoinWalletService()
