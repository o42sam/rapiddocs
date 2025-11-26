"""
Paystack payment service for handling card and bank transfer payments
"""
import requests
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import PaymentError

logger = get_logger('paystack_service')


class PaystackService:
    """Service for interacting with Paystack API"""

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = settings.PAYSTACK_API_URL
        self.currency = settings.PAYSTACK_CURRENCY
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Paystack API"""
        url = f"{self.base_url}/{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            result = response.json()

            logger.debug(f"Paystack API response: {result}")
            return result

        except requests.exceptions.Timeout:
            logger.error(f"Paystack API timeout: {endpoint}")
            raise PaymentError("Payment service timeout. Please try again.")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Paystack API HTTP error: {e.response.text}")
            error_data = e.response.json() if e.response.content else {}
            error_message = error_data.get('message', 'Payment processing failed')
            raise PaymentError(error_message)
        except Exception as e:
            logger.error(f"Paystack API error: {str(e)}")
            raise PaymentError(f"Payment service error: {str(e)}")

    def generate_reference(self, prefix: str = "txn") -> str:
        """Generate unique transaction reference"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = secrets.token_hex(4)
        return f"{prefix}_{timestamp}_{random_str}"

    def kobo_to_naira(self, kobo: int) -> float:
        """Convert kobo to naira"""
        return kobo / 100

    def naira_to_kobo(self, naira: float) -> int:
        """Convert naira to kobo (smallest currency unit)"""
        return int(naira * 100)

    def initialize_transaction(
        self,
        email: str,
        amount: float,
        reference: str,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initialize a card payment transaction

        Args:
            email: Customer email
            amount: Amount in naira
            reference: Unique transaction reference
            callback_url: URL to redirect after payment
            metadata: Additional data to store with transaction

        Returns:
            Dict with authorization_url, access_code, and reference
        """
        logger.info(f"Initializing Paystack transaction: {reference}")

        # Convert amount to kobo
        amount_in_kobo = self.naira_to_kobo(amount)

        data = {
            "email": email,
            "amount": amount_in_kobo,
            "currency": self.currency,
            "reference": reference,
            "callback_url": callback_url or f"{settings.CORS_ORIGINS.split(',')[0]}/payment/verify",
            "metadata": metadata or {}
        }

        response = self._make_request("POST", "transaction/initialize", data)

        if not response.get("status"):
            raise PaymentError(response.get("message", "Failed to initialize payment"))

        result = response.get("data", {})
        logger.info(f"Transaction initialized successfully: {reference}")

        return {
            "authorization_url": result.get("authorization_url"),
            "access_code": result.get("access_code"),
            "reference": result.get("reference")
        }

    def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """
        Verify a transaction

        Args:
            reference: Transaction reference to verify

        Returns:
            Dict with transaction details
        """
        logger.info(f"Verifying Paystack transaction: {reference}")

        response = self._make_request("GET", f"transaction/verify/{reference}")

        if not response.get("status"):
            raise PaymentError(response.get("message", "Failed to verify payment"))

        data = response.get("data", {})

        # Extract relevant information
        result = {
            "status": data.get("status"),  # success, failed, abandoned
            "reference": data.get("reference"),
            "amount": self.kobo_to_naira(data.get("amount", 0)),
            "currency": data.get("currency"),
            "paid_at": data.get("paid_at"),
            "channel": data.get("channel"),  # card, bank, etc.
            "gateway_response": data.get("gateway_response"),
            "metadata": data.get("metadata", {})
        }

        logger.info(f"Transaction verified: {reference}, status={result['status']}")
        return result

    def create_dedicated_virtual_account(
        self,
        email: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        preferred_bank: str = "wema-bank",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a dedicated virtual account for a customer

        Args:
            email: Customer email
            first_name: Customer first name
            last_name: Customer last name
            phone: Customer phone number
            preferred_bank: Preferred bank slug (wema-bank, titan-paystack, etc.)
            metadata: Additional metadata

        Returns:
            Dict with virtual account details
        """
        logger.info(f"Creating dedicated virtual account for: {email}")

        data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "preferred_bank": preferred_bank,
            "metadata": metadata or {}
        }

        if phone:
            data["phone"] = phone

        response = self._make_request("POST", "dedicated_account", data)

        if not response.get("status"):
            raise PaymentError(response.get("message", "Failed to create virtual account"))

        account_data = response.get("data", {})

        result = {
            "id": account_data.get("id"),
            "account_number": account_data.get("account_number"),
            "account_name": account_data.get("account_name"),
            "bank_name": account_data.get("bank", {}).get("name"),
            "bank_slug": account_data.get("bank", {}).get("slug"),
            "assigned": account_data.get("assigned"),
            "currency": account_data.get("currency"),
            "metadata": account_data.get("metadata", {})
        }

        logger.info(f"Virtual account created: {result['account_number']}")
        return result

    def fetch_dedicated_account(self, account_id: str) -> Dict[str, Any]:
        """Fetch details of a dedicated virtual account"""
        logger.info(f"Fetching dedicated account: {account_id}")

        response = self._make_request("GET", f"dedicated_account/{account_id}")

        if not response.get("status"):
            raise PaymentError(response.get("message", "Failed to fetch account details"))

        account_data = response.get("data", {})

        return {
            "id": account_data.get("id"),
            "account_number": account_data.get("account_number"),
            "account_name": account_data.get("account_name"),
            "bank_name": account_data.get("bank", {}).get("name"),
            "assigned": account_data.get("assigned"),
            "active": account_data.get("active"),
            "currency": account_data.get("currency")
        }

    def list_dedicated_accounts(
        self,
        active: Optional[bool] = None,
        currency: Optional[str] = None
    ) -> list:
        """List all dedicated virtual accounts"""
        params = {}
        if active is not None:
            params["active"] = str(active).lower()
        if currency:
            params["currency"] = currency

        response = self._make_request("GET", "dedicated_account", params=params)

        if not response.get("status"):
            return []

        return response.get("data", [])

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Paystack webhook signature

        Args:
            payload: Raw request body bytes
            signature: X-Paystack-Signature header value

        Returns:
            True if signature is valid, False otherwise
        """
        if not settings.PAYSTACK_WEBHOOK_SECRET:
            logger.warning("PAYSTACK_WEBHOOK_SECRET not configured")
            return False

        # Compute HMAC
        computed_signature = hmac.new(
            settings.PAYSTACK_WEBHOOK_SECRET.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha512
        ).hexdigest()

        # Compare signatures
        is_valid = hmac.compare_digest(computed_signature, signature)

        if not is_valid:
            logger.warning("Invalid webhook signature")

        return is_valid


# Singleton instance
paystack_service = PaystackService()
