#!/usr/bin/env python3
"""
Bitcoin Payment Flow Test Script
Tests the complete Bitcoin payment integration programmatically
"""

import asyncio
import requests
import time
from datetime import datetime
from typing import Dict, Optional
from bit import PrivateKeyTestnet
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init(autoreset=True)

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "btc_test@example.com"
TEST_USER_PASSWORD = "SecurePassword123!"
PACKAGE_TYPE = "small"  # small, medium, or large

# Test wallet with funds (you'll need to fund this from a faucet)
# Generate a new one or use existing testnet wallet with funds
TEST_WALLET_PRIVATE_KEY = None  # Will be generated if None


class BitcoinPaymentTester:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.payment_id: Optional[str] = None
        self.payment_address: Optional[str] = None
        self.amount_btc: float = 0
        self.test_wallet: Optional[PrivateKeyTestnet] = None

    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}{text.center(70)}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

    def print_step(self, step_num: int, text: str):
        """Print a test step"""
        print(f"{Fore.YELLOW}[Step {step_num}] {text}{Style.RESET_ALL}")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

    def print_error(self, text: str):
        """Print error message"""
        print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

    def print_info(self, text: str):
        """Print info message"""
        print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")

    def register_or_login(self) -> bool:
        """Register a test user or login if already exists"""
        self.print_step(1, "Registering/Logging in test user")

        # Try to register
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.print_success(f"Registered new user: {TEST_USER_EMAIL}")
                self.print_info(f"User ID: {self.user_id}")
                self.print_info(f"Initial Credits: {data['user']['credits']}")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                # User exists, try login
                self.print_info("User already exists, logging in...")
                return self.login()
            else:
                self.print_error(f"Registration failed: {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Registration error: {str(e)}")
            return False

    def login(self) -> bool:
        """Login with test credentials"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                data={
                    "username": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]

                # Get user profile
                profile_response = requests.get(
                    f"{API_BASE_URL}/auth/me",
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )

                if profile_response.status_code == 200:
                    user_data = profile_response.json()
                    self.user_id = user_data["id"]
                    self.print_success(f"Logged in as: {TEST_USER_EMAIL}")
                    self.print_info(f"Current Credits: {user_data['credits']}")
                    return True

            self.print_error(f"Login failed: {response.text}")
            return False
        except Exception as e:
            self.print_error(f"Login error: {str(e)}")
            return False

    def initiate_payment(self) -> bool:
        """Initiate a Bitcoin payment"""
        self.print_step(2, f"Initiating Bitcoin payment for '{PACKAGE_TYPE}' package")

        try:
            response = requests.post(
                f"{API_BASE_URL}/bitcoin/initiate",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={"package": PACKAGE_TYPE}
            )

            if response.status_code == 200:
                data = response.json()
                self.payment_id = data["payment_id"]
                self.payment_address = data["payment_address"]
                self.amount_btc = data["amount_btc"]

                self.print_success("Payment initiated successfully!")
                self.print_info(f"Payment ID: {self.payment_id}")
                self.print_info(f"Payment Address: {self.payment_address}")
                self.print_info(f"Amount Required: {self.amount_btc} BTC")
                self.print_info(f"Amount USD: ${data['amount_usd']}")
                self.print_info(f"Expires At: {data['expires_at']}")

                # Save QR code for reference
                print(f"\n{Fore.MAGENTA}QR Code Data Length: {len(data['qr_code_data'])} bytes{Style.RESET_ALL}\n")

                return True
            else:
                self.print_error(f"Payment initiation failed: {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Payment initiation error: {str(e)}")
            return False

    def setup_test_wallet(self) -> bool:
        """Setup test wallet for sending payment"""
        self.print_step(3, "Setting up test wallet")

        try:
            global TEST_WALLET_PRIVATE_KEY

            if TEST_WALLET_PRIVATE_KEY:
                self.test_wallet = PrivateKeyTestnet(TEST_WALLET_PRIVATE_KEY)
                self.print_success(f"Loaded existing wallet: {self.test_wallet.address}")
            else:
                # Generate new wallet
                self.test_wallet = PrivateKeyTestnet()
                TEST_WALLET_PRIVATE_KEY = self.test_wallet.to_wif()
                self.print_success(f"Generated new wallet: {self.test_wallet.address}")
                self.print_info(f"Private Key (WIF): {TEST_WALLET_PRIVATE_KEY}")
                print(f"\n{Fore.RED}IMPORTANT: Save this private key for future tests!{Style.RESET_ALL}")
                print(f"{Fore.RED}Fund this address from a testnet faucet: {self.test_wallet.address}{Style.RESET_ALL}\n")

            # Check balance
            balance = self.test_wallet.get_balance('btc')
            self.print_info(f"Wallet Balance: {balance} BTC")

            if balance < self.amount_btc:
                self.print_error(f"Insufficient balance! Need {self.amount_btc} BTC, have {balance} BTC")
                print(f"\n{Fore.YELLOW}Get testnet Bitcoin from:{Style.RESET_ALL}")
                print("  - https://testnet-faucet.mempool.co/")
                print("  - https://coinfaucet.eu/en/btc-testnet/")
                print(f"\nSend to: {self.test_wallet.address}\n")
                return False

            return True
        except Exception as e:
            self.print_error(f"Wallet setup error: {str(e)}")
            return False

    def send_payment(self) -> bool:
        """Send Bitcoin payment to the generated address"""
        self.print_step(4, "Sending Bitcoin payment")

        try:
            # Create transaction
            tx_hash = self.test_wallet.send(
                [(self.payment_address, self.amount_btc, 'btc')],
                fee=50,  # 50 satoshis per byte
                absolute_fee=False
            )

            self.print_success(f"Payment sent successfully!")
            self.print_info(f"Transaction Hash: {tx_hash}")
            self.print_info(f"Blockstream Explorer: https://blockstream.info/testnet/tx/{tx_hash}")

            return True
        except Exception as e:
            self.print_error(f"Payment sending error: {str(e)}")
            return False

    def check_payment_status(self) -> Dict:
        """Check the current payment status"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/bitcoin/status",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={"payment_id": self.payment_id}
            )

            if response.status_code == 200:
                return response.json()
            else:
                self.print_error(f"Status check failed: {response.text}")
                return {}
        except Exception as e:
            self.print_error(f"Status check error: {str(e)}")
            return {}

    def monitor_payment(self, timeout_seconds: int = 3600) -> bool:
        """Monitor payment until confirmed or timeout"""
        self.print_step(5, "Monitoring payment confirmations")

        start_time = time.time()
        last_status = None
        last_confirmations = 0

        while time.time() - start_time < timeout_seconds:
            status_data = self.check_payment_status()

            if not status_data:
                time.sleep(10)
                continue

            current_status = status_data.get("status")
            confirmations = status_data.get("confirmations", 0)
            required_confirmations = status_data.get("required_confirmations", 3)

            # Print status if changed
            if current_status != last_status or confirmations != last_confirmations:
                elapsed = int(time.time() - start_time)

                print(f"\n{Fore.CYAN}[{elapsed}s] Status: {current_status.upper()}{Style.RESET_ALL}")

                if confirmations > 0:
                    progress = (confirmations / required_confirmations) * 100
                    bar_length = 30
                    filled = int(bar_length * confirmations / required_confirmations)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    print(f"{Fore.GREEN}Confirmations: [{bar}] {confirmations}/{required_confirmations} ({progress:.0f}%){Style.RESET_ALL}")

                if status_data.get("tx_hash"):
                    print(f"{Fore.BLUE}TX: https://blockstream.info/testnet/tx/{status_data['tx_hash']}{Style.RESET_ALL}")

                print(f"{Fore.YELLOW}{status_data.get('message', '')}{Style.RESET_ALL}")

                last_status = current_status
                last_confirmations = confirmations

            # Check if confirmed
            if current_status == "confirmed":
                self.print_success(f"Payment confirmed with {confirmations} confirmations!")
                return True

            # Check if failed or expired
            if current_status in ["failed", "expired"]:
                self.print_error(f"Payment {current_status}: {status_data.get('message', '')}")
                return False

            # Wait before next check
            time.sleep(10)

        self.print_error(f"Monitoring timed out after {timeout_seconds} seconds")
        return False

    def confirm_and_process(self) -> bool:
        """Confirm payment and process credits"""
        self.print_step(6, "Confirming payment and processing credits")

        try:
            response = requests.post(
                f"{API_BASE_URL}/bitcoin/confirm/{self.payment_id}",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )

            if response.status_code == 200:
                data = response.json()
                self.print_success("Payment processed successfully!")
                self.print_info(f"Credits Added: {data['credits_added']}")
                self.print_info(f"New Balance: {data['new_balance']}")
                self.print_info(f"Transaction Hash: {data['tx_hash']}")
                return True
            else:
                self.print_error(f"Payment confirmation failed: {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Payment confirmation error: {str(e)}")
            return False

    def verify_credits(self) -> bool:
        """Verify credits were added to account"""
        self.print_step(7, "Verifying final credits balance")

        try:
            response = requests.get(
                f"{API_BASE_URL}/auth/me",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )

            if response.status_code == 200:
                user_data = response.json()
                self.print_success(f"Final Credits Balance: {user_data['credits']}")
                return True
            else:
                self.print_error(f"Failed to verify credits: {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Verification error: {str(e)}")
            return False

    async def run_full_test(self):
        """Run the complete Bitcoin payment test flow"""
        self.print_header("BITCOIN PAYMENT FLOW TEST")

        print(f"{Fore.MAGENTA}Test Configuration:{Style.RESET_ALL}")
        print(f"  API URL: {API_BASE_URL}")
        print(f"  User: {TEST_USER_EMAIL}")
        print(f"  Package: {PACKAGE_TYPE}")
        print(f"  Timestamp: {datetime.utcnow().isoformat()}\n")

        # Step 1: Register/Login
        if not self.register_or_login():
            self.print_error("Failed to register/login. Aborting test.")
            return False

        # Step 2: Initiate Payment
        if not self.initiate_payment():
            self.print_error("Failed to initiate payment. Aborting test.")
            return False

        # Step 3: Setup Test Wallet
        if not self.setup_test_wallet():
            self.print_error("Failed to setup test wallet. Aborting test.")
            self.print_info("You can resume this test later after funding the wallet")
            self.print_info(f"Payment ID to resume: {self.payment_id}")
            return False

        # Step 4: Send Payment
        user_input = input(f"\n{Fore.YELLOW}Send {self.amount_btc} BTC from test wallet? (y/n): {Style.RESET_ALL}").lower()
        if user_input != 'y':
            self.print_info("Payment sending skipped. You can send manually and continue monitoring.")
            self.print_info(f"Send {self.amount_btc} BTC to: {self.payment_address}")
        else:
            if not self.send_payment():
                self.print_error("Failed to send payment. Aborting test.")
                return False

        # Step 5: Monitor Payment
        if not self.monitor_payment(timeout_seconds=3600):  # 1 hour timeout
            self.print_error("Payment monitoring failed or timed out.")
            return False

        # Step 6: Confirm and Process
        if not self.confirm_and_process():
            self.print_error("Failed to confirm and process payment.")
            return False

        # Step 7: Verify Credits
        if not self.verify_credits():
            self.print_error("Failed to verify credits.")
            return False

        # Success!
        self.print_header("TEST COMPLETED SUCCESSFULLY!")
        return True


async def main():
    """Main test runner"""
    tester = BitcoinPaymentTester()

    try:
        success = await tester.run_full_test()

        if success:
            print(f"\n{Fore.GREEN}{'='*70}")
            print(f"{Fore.GREEN}ALL TESTS PASSED!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*70}\n")
        else:
            print(f"\n{Fore.RED}{'='*70}")
            print(f"{Fore.RED}TEST FAILED{Style.RESET_ALL}")
            print(f"{Fore.RED}{'='*70}\n")
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Test interrupted by user{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    asyncio.run(main())
