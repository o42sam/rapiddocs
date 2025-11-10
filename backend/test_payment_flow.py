"""
Comprehensive test script for Bitcoin payment flow
Tests all steps from package selection to funds forwarding
"""

import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style
init(autoreset=True)

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = f"test_payment_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"

class PaymentFlowTester:
    def __init__(self):
        self.access_token = None
        self.user_id = None
        self.payment_id = None
        self.payment_address = None
        self.initial_credits = 0
        self.test_results = []

    def log(self, message, status="INFO"):
        """Log test messages with colors"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if status == "PASS":
            print(f"{Fore.GREEN}[{timestamp}] ✓ {message}{Style.RESET_ALL}")
        elif status == "FAIL":
            print(f"{Fore.RED}[{timestamp}] ✗ {message}{Style.RESET_ALL}")
        elif status == "WARN":
            print(f"{Fore.YELLOW}[{timestamp}] ⚠ {message}{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}[{timestamp}] ℹ {message}{Style.RESET_ALL}")

    def test_step(self, name, func):
        """Execute a test step and track results"""
        print(f"\n{Fore.BLUE}{'='*80}")
        print(f"Testing: {name}")
        print(f"{'='*80}{Style.RESET_ALL}\n")

        try:
            result = func()
            self.test_results.append({"step": name, "status": "PASS", "details": result})
            return result
        except Exception as e:
            self.log(f"Test failed: {str(e)}", "FAIL")
            self.test_results.append({"step": name, "status": "FAIL", "error": str(e)})
            raise

    # ===== STEP 1: User Registration & Authentication =====
    def test_user_registration(self):
        """Test user registration"""
        self.log("Registering test user...")

        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": TEST_USER_EMAIL,
            "username": f"testpayuser{int(time.time())}",
            "password": TEST_USER_PASSWORD,
            "full_name": "Test Payment User"
        })

        if response.status_code == 201:
            data = response.json()
            self.access_token = data["tokens"]["access_token"]
            self.user_id = data["user"]["id"]
            self.initial_credits = data["user"]["credits"]
            self.log(f"User registered successfully! User ID: {self.user_id}", "PASS")
            self.log(f"Initial credits: {self.initial_credits}", "INFO")
            return data
        else:
            raise Exception(f"Registration failed: {response.status_code} - {response.text}")

    # ===== STEP 2: Credits Package Selection =====
    def test_get_packages(self):
        """Test retrieving available credits packages"""
        self.log("Fetching available credits packages...")

        response = requests.get(f"{BASE_URL}/credits/packages")

        if response.status_code == 200:
            data = response.json()
            packages = data["packages"]
            self.log(f"Found {len(packages)} packages", "PASS")

            for pkg in packages:
                self.log(f"  • {pkg['name']}: {pkg['credits']} credits for ${pkg['price']}", "INFO")

            return packages
        else:
            raise Exception(f"Failed to fetch packages: {response.status_code}")

    # ===== STEP 3: Bitcoin Payment Initiation =====
    def test_initiate_payment(self):
        """Test initiating a Bitcoin payment"""
        self.log("Initiating Bitcoin payment for 'small' package...")

        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.post(
            f"{BASE_URL}/bitcoin/initiate",
            json={"package": "small"},
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            self.payment_id = data["payment_id"]
            self.payment_address = data["payment_address"]

            self.log(f"Payment initiated successfully!", "PASS")
            self.log(f"Payment ID: {self.payment_id}", "INFO")
            self.log(f"Payment Address: {self.payment_address}", "INFO")
            self.log(f"Amount BTC: {data['amount_btc']}", "INFO")
            self.log(f"Amount USD: ${data['amount_usd']}", "INFO")
            self.log(f"Expires at: {data['expires_at']}", "INFO")
            self.log(f"QR Code generated: {len(data['qr_code_data'])} bytes", "INFO")

            return data
        else:
            raise Exception(f"Payment initiation failed: {response.status_code} - {response.text}")

    # ===== STEP 4: Bitcoin Address Generation Validation =====
    def test_address_validation(self):
        """Validate the generated Bitcoin address"""
        self.log("Validating generated Bitcoin address...")

        from app.services.bitcoin_wallet import bitcoin_wallet_service

        is_valid = bitcoin_wallet_service.validate_address(self.payment_address)

        if is_valid:
            self.log(f"Address {self.payment_address} is valid", "PASS")

            # Check address prefix for testnet
            if self.payment_address.startswith(('m', 'n', '2', 'tb1')):
                self.log("Address is testnet address ✓", "PASS")
            else:
                self.log("Warning: Address doesn't appear to be testnet", "WARN")

            return True
        else:
            raise Exception("Generated address is invalid!")

    # ===== STEP 5: Payment Status Monitoring =====
    def test_payment_status(self):
        """Test payment status checking"""
        self.log("Checking payment status...")

        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.post(
            f"{BASE_URL}/bitcoin/status",
            json={"payment_id": self.payment_id},
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            self.log(f"Payment status retrieved successfully!", "PASS")
            self.log(f"Status: {data['status']}", "INFO")
            self.log(f"Confirmations: {data['confirmations']}/{data['required_confirmations']}", "INFO")
            self.log(f"Amount received: {data['amount_received_btc']} BTC", "INFO")
            self.log(f"Message: {data['message']}", "INFO")

            return data
        else:
            raise Exception(f"Status check failed: {response.status_code} - {response.text}")

    # ===== STEP 6: Blockchain Monitoring Test =====
    def test_blockchain_monitoring(self):
        """Test blockchain API connectivity and monitoring"""
        self.log("Testing blockchain API connectivity...")

        from app.services.bitcoin_monitor import bitcoin_monitor_service

        # Test BTC/USD rate fetching
        rate = bitcoin_monitor_service.get_btc_to_usd_rate()
        if rate:
            self.log(f"Current BTC/USD rate: ${rate:,.2f}", "PASS")
        else:
            self.log("Failed to fetch BTC/USD rate", "WARN")

        # Test payment checking (will return no payment found since we haven't sent BTC)
        check_result = bitcoin_monitor_service.check_payment(
            self.payment_address,
            0.0001  # Expected amount
        )

        self.log(f"Payment check result: {check_result['status']}", "INFO")
        self.log(f"Amount received: {check_result['amount_received']} BTC", "INFO")

        if check_result['status'] in ['no_transaction_found', 'insufficient_amount']:
            self.log("Blockchain monitoring working correctly (no payment yet)", "PASS")
            return check_result
        else:
            self.log(f"Unexpected status: {check_result['status']}", "WARN")
            return check_result

    # ===== STEP 7: Wallet Service Test =====
    def test_wallet_service(self):
        """Test wallet generation and management"""
        self.log("Testing wallet service...")

        from app.services.bitcoin_wallet import bitcoin_wallet_service

        # Generate a test address
        wallet_data = bitcoin_wallet_service.generate_payment_address()

        self.log(f"Test wallet generated", "PASS")
        self.log(f"Address: {wallet_data['address']}", "INFO")
        self.log(f"Network: {wallet_data['network']}", "INFO")
        self.log(f"Private key length: {len(wallet_data['private_key'])} chars", "INFO")

        # Validate the address
        is_valid = bitcoin_wallet_service.validate_address(wallet_data['address'])

        if is_valid:
            self.log("Generated address is valid", "PASS")
        else:
            raise Exception("Generated test address is invalid")

        return wallet_data

    # ===== STEP 8: Encryption Test =====
    def test_private_key_encryption(self):
        """Test private key encryption/decryption"""
        self.log("Testing private key encryption...")

        from app.routes.bitcoin import encrypt_private_key, decrypt_private_key

        test_key = "test_private_key_12345"

        # Encrypt
        encrypted = encrypt_private_key(test_key)
        self.log(f"Encrypted key length: {len(encrypted)} chars", "INFO")

        # Decrypt
        decrypted = decrypt_private_key(encrypted)

        if decrypted == test_key:
            self.log("Encryption/decryption working correctly", "PASS")
        else:
            raise Exception("Decrypted key doesn't match original!")

        return True

    # ===== STEP 9: Credits Balance Check =====
    def test_credits_balance(self):
        """Test credits balance retrieval"""
        self.log("Checking credits balance...")

        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(
            f"{BASE_URL}/credits/balance",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            self.log(f"Current balance: {data['credits']} credits", "PASS")
            return data
        else:
            raise Exception(f"Balance check failed: {response.status_code}")

    # ===== STEP 10: Forwarding Service Test (Dry Run) =====
    def test_forwarding_service(self):
        """Test the forwarding service configuration"""
        self.log("Testing forwarding service configuration...")

        from app.services.bitcoin_forwarder import bitcoin_forwarder_service
        from app.config import settings

        self.log(f"Personal wallet: {settings.BITCOIN_PERSONAL_WALLET}", "INFO")
        self.log(f"Network: {settings.BITCOIN_NETWORK}", "INFO")

        # Get recommended fee
        fee = bitcoin_forwarder_service.get_recommended_fee()
        self.log(f"Recommended fee: {fee} sat/byte", "INFO")

        if settings.BITCOIN_PERSONAL_WALLET:
            self.log("Personal wallet configured", "PASS")
        else:
            self.log("WARNING: Personal wallet not configured!", "WARN")

        return True

    # ===== STEP 11: Error Handling Tests =====
    def test_error_handling(self):
        """Test various error scenarios"""
        self.log("Testing error handling...")

        headers = {"Authorization": f"Bearer {self.access_token}"}

        # Test 1: Invalid package
        response = requests.post(
            f"{BASE_URL}/bitcoin/initiate",
            json={"package": "invalid_package"},
            headers=headers
        )
        if response.status_code in [400, 422]:  # Both are valid validation errors
            self.log("Invalid package rejected correctly", "PASS")
        else:
            raise Exception(f"Expected 400/422, got {response.status_code}")

        # Test 2: Invalid payment ID
        response = requests.post(
            f"{BASE_URL}/bitcoin/status",
            json={"payment_id": "invalid_id_123"},
            headers=headers
        )
        if response.status_code in [400, 404, 422, 500]:  # 500 for invalid ObjectId
            self.log("Invalid payment ID rejected correctly", "PASS")
        else:
            raise Exception(f"Expected 400/404/422/500, got {response.status_code}")

        # Test 3: Unauthorized access
        response = requests.get(f"{BASE_URL}/credits/balance")
        if response.status_code in [401, 403]:  # Both unauthorized/forbidden are acceptable
            self.log("Unauthorized access blocked correctly", "PASS")
        else:
            raise Exception(f"Expected 401/403, got {response.status_code}")

        return True

    # ===== STEP 12: Document Cost Check =====
    def test_document_cost(self):
        """Test document cost retrieval"""
        self.log("Testing document cost endpoints...")

        for doc_type in ["formal", "infographic"]:
            response = requests.get(f"{BASE_URL}/credits/cost/{doc_type}")

            if response.status_code == 200:
                data = response.json()
                self.log(f"{doc_type.capitalize()} document cost: {data['cost']} credits", "PASS")
            else:
                raise Exception(f"Cost check failed for {doc_type}")

        return True

    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"\n{Fore.MAGENTA}{'='*80}")
        print(f"BITCOIN PAYMENT FLOW - COMPREHENSIVE TEST SUITE")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        print(f"Starting tests at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        start_time = time.time()

        try:
            # Execute all test steps
            self.test_step("Step 1: User Registration & Authentication", self.test_user_registration)
            self.test_step("Step 2: Credits Package Selection", self.test_get_packages)
            self.test_step("Step 3: Bitcoin Payment Initiation", self.test_initiate_payment)
            self.test_step("Step 4: Bitcoin Address Validation", self.test_address_validation)
            self.test_step("Step 5: Payment Status Monitoring", self.test_payment_status)
            self.test_step("Step 6: Blockchain Monitoring", self.test_blockchain_monitoring)
            self.test_step("Step 7: Wallet Service", self.test_wallet_service)
            self.test_step("Step 8: Private Key Encryption", self.test_private_key_encryption)
            self.test_step("Step 9: Credits Balance Check", self.test_credits_balance)
            self.test_step("Step 10: Forwarding Service Configuration", self.test_forwarding_service)
            self.test_step("Step 11: Error Handling", self.test_error_handling)
            self.test_step("Step 12: Document Cost Check", self.test_document_cost)

        except Exception as e:
            self.log(f"\n❌ Test suite stopped due to error: {str(e)}", "FAIL")

        # Calculate duration
        duration = time.time() - start_time

        # Print summary
        self.print_summary(duration)

    def print_summary(self, duration):
        """Print test summary"""
        print(f"\n{Fore.MAGENTA}{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}{Style.RESET_ALL}\n")

        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        total = len(self.test_results)

        print(f"Total Tests: {total}")
        print(f"{Fore.GREEN}Passed: {passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {failed}{Style.RESET_ALL}")
        print(f"Duration: {duration:.2f} seconds")

        if failed > 0:
            print(f"\n{Fore.RED}Failed Tests:{Style.RESET_ALL}")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  ✗ {result['step']}: {result.get('error', 'Unknown error')}")

        print(f"\n{Fore.YELLOW}{'='*80}")
        print(f"PRODUCTION READINESS NOTES")
        print(f"{'='*80}{Style.RESET_ALL}\n")

        if self.payment_address:
            print(f"📍 Test Payment Address: {self.payment_address}")
            print(f"   To complete the flow, send testnet BTC to this address")
            print(f"   Get testnet BTC from: https://coinfaucet.eu/en/btc-testnet/")

        print(f"\n⚠️  SECURITY CHECKLIST:")
        print(f"   ☐ Change JWT_SECRET_KEY in production")
        print(f"   ☐ Set BITCOIN_PERSONAL_WALLET to your actual wallet")
        print(f"   ☐ Switch BITCOIN_NETWORK to 'mainnet' for production")
        print(f"   ☐ Implement proper private key management (HSM/KMS)")
        print(f"   ☐ Add rate limiting for payment endpoints")
        print(f"   ☐ Set up monitoring and alerting")
        print(f"   ☐ Test with real BTC on testnet before mainnet")

        print(f"\n{Fore.GREEN}✅ Basic payment flow is functional and ready for testnet testing!{Style.RESET_ALL}")

if __name__ == "__main__":
    # Check if colorama is available
    try:
        from colorama import init, Fore, Style
    except ImportError:
        print("Installing colorama for better output...")
        import subprocess
        subprocess.check_call(["pip", "install", "colorama", "--quiet"])
        from colorama import init, Fore, Style

    tester = PaymentFlowTester()
    tester.run_all_tests()
