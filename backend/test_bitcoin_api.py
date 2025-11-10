#!/usr/bin/env python3
"""
Bitcoin Payment API Test Script
Tests the API endpoints without sending actual Bitcoin
"""

import requests
import time
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = f"test_user_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "SecurePassword123!"


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text.center(70)}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def print_step(step_num: int, text: str):
    """Print a test step"""
    print(f"{Fore.YELLOW}[Step {step_num}] {text}{Style.RESET_ALL}")


def print_success(text: str):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")


def print_error(text: str):
    """Print error message"""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")


def print_info(text: str):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")


def test_user_registration():
    """Test user registration"""
    print_step(1, "Testing User Registration")

    try:
        username = f"user_{int(time.time())}"
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "email": TEST_USER_EMAIL,
                "username": username,
                "password": TEST_USER_PASSWORD
            }
        )

        if response.status_code == 201:
            data = response.json()
            print_success("User registered successfully!")
            print_info(f"Email: {TEST_USER_EMAIL}")
            print_info(f"User ID: {data['user']['id']}")
            print_info(f"Initial Credits: {data['user']['credits']}")
            print_info(f"Access Token: {data['tokens']['access_token'][:20]}...")
            return data['tokens']['access_token']
        else:
            print_error(f"Registration failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return None


def test_payment_initiation(access_token: str, package: str = "small"):
    """Test Bitcoin payment initiation"""
    print_step(2, f"Testing Payment Initiation ({package} package)")

    try:
        response = requests.post(
            f"{API_BASE_URL}/bitcoin/initiate",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"package": package}
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Payment initiated successfully!")
            print_info(f"Payment ID: {data['payment_id']}")
            print_info(f"Payment Address: {data['payment_address']}")
            print_info(f"Amount BTC: {data['amount_btc']}")
            print_info(f"Amount USD: ${data['amount_usd']}")
            print_info(f"QR Code: {len(data['qr_code_data'])} bytes")
            print_info(f"Expires At: {data['expires_at']}")
            print_info(f"Message: {data['message']}")

            # Verify address format
            if data['payment_address'].startswith('tb1') or data['payment_address'].startswith('m') or data['payment_address'].startswith('n'):
                print_success("Address format is valid (testnet)")
            else:
                print_error("Address format looks incorrect for testnet")

            return data['payment_id'], data['payment_address'], data['amount_btc']
        else:
            print_error(f"Payment initiation failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None, None, None
    except Exception as e:
        print_error(f"Payment initiation error: {str(e)}")
        return None, None, None


def test_payment_status(access_token: str, payment_id: str):
    """Test payment status check"""
    print_step(3, "Testing Payment Status Check")

    try:
        response = requests.post(
            f"{API_BASE_URL}/bitcoin/status",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"payment_id": payment_id}
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Status check successful!")
            print_info(f"Status: {data['status']}")
            print_info(f"Payment Address: {data['payment_address']}")
            print_info(f"Amount BTC: {data['amount_btc']}")
            print_info(f"Amount Received: {data['amount_received_btc']} BTC")
            print_info(f"Confirmations: {data['confirmations']}/{data['required_confirmations']}")
            print_info(f"TX Hash: {data.get('tx_hash', 'None')}")
            print_info(f"Message: {data['message']}")
            return data
        else:
            print_error(f"Status check failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Status check error: {str(e)}")
        return None


def test_multiple_payments(access_token: str):
    """Test initiating multiple payments"""
    print_step(4, "Testing Multiple Payment Initiation")

    packages = ["small", "medium", "large"]
    payment_ids = []

    for package in packages:
        try:
            response = requests.post(
                f"{API_BASE_URL}/bitcoin/initiate",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"package": package}
            )

            if response.status_code == 200:
                data = response.json()
                payment_ids.append(data['payment_id'])
                print_success(f"{package.capitalize()} package: {data['amount_btc']} BTC (${data['amount_usd']})")
            else:
                print_error(f"Failed to initiate {package} package")
        except Exception as e:
            print_error(f"Error with {package} package: {str(e)}")

    print_info(f"Created {len(payment_ids)} payment records")
    return payment_ids


def test_invalid_package(access_token: str):
    """Test with invalid package"""
    print_step(5, "Testing Invalid Package Error Handling")

    try:
        response = requests.post(
            f"{API_BASE_URL}/bitcoin/initiate",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"package": "invalid_package"}
        )

        if response.status_code == 400:
            print_success("Correctly rejected invalid package!")
            print_info(f"Error message: {response.json().get('detail', 'N/A')}")
        else:
            print_error(f"Expected 400 error, got: {response.status_code}")
    except Exception as e:
        print_error(f"Error handling test failed: {str(e)}")


def test_unauthorized_access():
    """Test without authentication"""
    print_step(6, "Testing Unauthorized Access Protection")

    try:
        response = requests.post(
            f"{API_BASE_URL}/bitcoin/initiate",
            json={"package": "small"}
        )

        if response.status_code == 401:
            print_success("Correctly rejected unauthorized request!")
        else:
            print_error(f"Expected 401 error, got: {response.status_code}")
    except Exception as e:
        print_error(f"Unauthorized test failed: {str(e)}")


def test_wallet_address_uniqueness(access_token: str):
    """Test that each payment gets a unique address"""
    print_step(7, "Testing Wallet Address Uniqueness")

    addresses = set()

    for i in range(5):
        try:
            response = requests.post(
                f"{API_BASE_URL}/bitcoin/initiate",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"package": "small"}
            )

            if response.status_code == 200:
                data = response.json()
                addresses.add(data['payment_address'])
        except Exception as e:
            print_error(f"Request {i+1} failed: {str(e)}")

    if len(addresses) == 5:
        print_success("All 5 payment addresses are unique!")
        print_info(f"Sample addresses:")
        for i, addr in enumerate(list(addresses)[:3], 1):
            print(f"    {i}. {addr}")
    else:
        print_error(f"Address uniqueness test failed! Only {len(addresses)}/5 unique")


def test_btc_usd_conversion(access_token: str):
    """Test BTC/USD rate conversion"""
    print_step(8, "Testing BTC/USD Rate Conversion")

    try:
        # Get current BTC rate from CoinGecko
        rate_response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"}
        )

        if rate_response.status_code == 200:
            btc_usd_rate = rate_response.json()["bitcoin"]["usd"]
            print_info(f"Current BTC/USD rate: ${btc_usd_rate:,.2f}")

            # Initiate payment
            payment_response = requests.post(
                f"{API_BASE_URL}/bitcoin/initiate",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"package": "small"}
            )

            if payment_response.status_code == 200:
                data = payment_response.json()
                calculated_usd = data['amount_btc'] * btc_usd_rate
                print_info(f"Package price: ${data['amount_usd']}")
                print_info(f"BTC amount: {data['amount_btc']}")
                print_info(f"Calculated USD: ${calculated_usd:.2f}")

                # Allow 1% difference for rate fluctuation
                difference_pct = abs(calculated_usd - data['amount_usd']) / data['amount_usd'] * 100
                if difference_pct < 1:
                    print_success(f"Conversion is accurate (within {difference_pct:.2f}%)")
                else:
                    print_error(f"Conversion seems off ({difference_pct:.2f}% difference)")
        else:
            print_error("Could not fetch BTC rate from CoinGecko")
    except Exception as e:
        print_error(f"Conversion test error: {str(e)}")


def test_api_documentation():
    """Test that API documentation is accessible"""
    print_step(9, "Testing API Documentation Accessibility")

    try:
        response = requests.get(f"{API_BASE_URL}/docs")

        if response.status_code == 200:
            print_success("API documentation is accessible!")
            print_info(f"Docs URL: {API_BASE_URL}/docs")
        else:
            print_error(f"Documentation not accessible: {response.status_code}")
    except Exception as e:
        print_error(f"Documentation test error: {str(e)}")


def main():
    """Run all API tests"""
    print_header("BITCOIN PAYMENT API TEST SUITE")

    print(f"{Fore.MAGENTA}Configuration:{Style.RESET_ALL}")
    print(f"  API Base URL: {API_BASE_URL}")
    print(f"  Test Time: {datetime.utcnow().isoformat()}")
    print()

    # Test 1: User Registration
    access_token = test_user_registration()
    if not access_token:
        print_error("Cannot continue without access token")
        return

    # Test 2: Payment Initiation
    payment_id, payment_address, amount_btc = test_payment_initiation(access_token)
    if not payment_id:
        print_error("Payment initiation failed")
        return

    # Test 3: Payment Status
    test_payment_status(access_token, payment_id)

    # Test 4: Multiple Payments
    test_multiple_payments(access_token)

    # Test 5: Invalid Package
    test_invalid_package(access_token)

    # Test 6: Unauthorized Access
    test_unauthorized_access()

    # Test 7: Address Uniqueness
    test_wallet_address_uniqueness(access_token)

    # Test 8: BTC/USD Conversion
    test_btc_usd_conversion(access_token)

    # Test 9: API Documentation
    test_api_documentation()

    # Summary
    print_header("TEST SUITE COMPLETED")
    print(f"{Fore.GREEN}All API endpoint tests completed!{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Next Steps:{Style.RESET_ALL}")
    print("  1. Send testnet Bitcoin to one of the generated addresses")
    print("  2. Monitor payment status with the status endpoint")
    print("  3. After 3 confirmations, call the confirm endpoint")
    print(f"\n{Fore.BLUE}Payment Details:{Style.RESET_ALL}")
    print(f"  Payment ID: {payment_id}")
    print(f"  Address: {payment_address}")
    print(f"  Amount: {amount_btc} BTC")
    print(f"\n{Fore.CYAN}Get testnet Bitcoin from:{Style.RESET_ALL}")
    print("  - https://testnet-faucet.mempool.co/")
    print("  - https://coinfaucet.eu/en/btc-testnet/")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Tests interrupted by user{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}\n")
        import traceback
        traceback.print_exc()
