#!/bin/bash

# Test script for Kali Linux compatibility checks

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test functions
log_info() {
    echo -e "${GREEN}[TEST]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test OS detection
test_os_detection() {
    log_info "Testing OS detection..."

    OS_ID=$(lsb_release -si 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo "unknown")
    OS_CODENAME=$(lsb_release -cs 2>/dev/null || echo "unknown")
    OS_VERSION=$(lsb_release -sr 2>/dev/null || echo "unknown")

    echo "  OS ID: $OS_ID"
    echo "  OS Codename: $OS_CODENAME"
    echo "  OS Version: $OS_VERSION"

    if [[ "$OS_ID" == "kali" ]]; then
        log_info "✓ Kali Linux correctly detected"
        return 0
    else
        log_error "✗ OS detection failed or not Kali Linux"
        return 1
    fi
}

# Test package availability
test_package_availability() {
    log_info "Testing package availability on Kali..."

    PACKAGES_TO_TEST=(
        "python3"
        "python3-venv"
        "python3-dev"
        "build-essential"
        "git"
        "nginx"
        "curl"
        "wget"
        "vim"
        "tmux"
        "lsb-release"
        "gnupg"
        "htop"
        "ncdu"
        "postgresql"
        "redis-server"
        "ufw"
        "supervisor"
        "certbot"
        "fail2ban"
    )

    for pkg in "${PACKAGES_TO_TEST[@]}"; do
        if apt-cache show "$pkg" &>/dev/null; then
            echo "  ✓ $pkg - available"
        else
            echo "  ✗ $pkg - NOT available"
        fi
    done
}

# Test MongoDB client options
test_mongodb_options() {
    log_info "Testing MongoDB client installation options..."

    # Check if MongoDB clients are available in repos
    if apt-cache show mongodb-clients &>/dev/null; then
        echo "  ✓ mongodb-clients available in repository"
    else
        echo "  ✗ mongodb-clients NOT available in repository"
    fi

    # Check if npm is available for mongosh
    if command -v npm &>/dev/null; then
        echo "  ✓ npm available (can install mongosh via npm)"
    else
        echo "  ✗ npm NOT available"
    fi

    # Check if snap is available
    if command -v snap &>/dev/null; then
        echo "  ✓ snap available (can install certbot via snap)"
    else
        echo "  ✗ snap NOT available"
    fi
}

# Test firewall options
test_firewall_options() {
    log_info "Testing firewall options..."

    if command -v ufw &>/dev/null; then
        echo "  ✓ UFW is installed"
    else
        echo "  ✗ UFW is NOT installed (will use iptables)"
    fi

    if command -v iptables &>/dev/null; then
        echo "  ✓ iptables is available"
    else
        echo "  ✗ iptables is NOT available"
    fi
}

# Test Python environment
test_python_env() {
    log_info "Testing Python environment setup..."

    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "  Python version: $PYTHON_VERSION"

    # Test creating a virtual environment
    TEST_VENV="/tmp/test-venv-$$"
    if python3 -m venv "$TEST_VENV" 2>/dev/null; then
        echo "  ✓ Can create Python virtual environments"
        rm -rf "$TEST_VENV"
    else
        echo "  ✗ Cannot create Python virtual environments"
    fi
}

# Main test execution
main() {
    echo "========================================="
    echo "     Kali Linux Setup Script Test"
    echo "========================================="
    echo ""

    test_os_detection
    echo ""
    test_package_availability
    echo ""
    test_mongodb_options
    echo ""
    test_firewall_options
    echo ""
    test_python_env
    echo ""

    echo "========================================="
    echo "Test complete. Review the results above."
    echo "========================================="
}

main "$@"