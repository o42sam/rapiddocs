#!/bin/bash

# DocGen Backend Deployment Script
# This script deploys the backend to a Hostinger VPS

set -e  # Exit on error

# Configuration
REMOTE_USER="docgen"
REMOTE_HOST="your-vps-ip"  # Replace with your VPS IP
REMOTE_DIR="/home/docgen/backend"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH="master"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    log_info "Checking requirements..."

    for tool in git ssh rsync; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool is not installed"
            exit 1
        fi
    done

    log_info "All requirements met"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --host)
                REMOTE_HOST="$2"
                shift 2
                ;;
            --user)
                REMOTE_USER="$2"
                shift 2
                ;;
            --branch)
                BRANCH="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --host <ip>      VPS IP address"
                echo "  --user <user>    SSH user (default: docgen)"
                echo "  --branch <name>  Git branch (default: master)"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

# Ensure we're on the correct branch
check_git_status() {
    log_info "Checking git status..."

    # Check for uncommitted changes
    if [[ -n $(git status -s) ]]; then
        log_warn "You have uncommitted changes. Commit or stash them before deploying."
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    # Fetch latest changes
    log_info "Fetching latest changes from remote..."
    git fetch origin

    # Check if we're behind remote
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/$BRANCH)

    if [ "$LOCAL" != "$REMOTE" ]; then
        log_warn "Local branch is not up to date with origin/$BRANCH"
        read -p "Pull latest changes? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git pull origin $BRANCH
        fi
    fi
}

# Build production files locally
build_production() {
    log_info "Building production files..."

    # Generate requirements file
    if [ -f "requirements-production.txt" ]; then
        log_info "Production requirements file found"
    else
        log_warn "Creating production requirements from requirements.txt"
        cp requirements.txt requirements-production.txt
    fi
}

# Deploy to VPS
deploy_to_vps() {
    log_info "Deploying to $REMOTE_HOST..."

    # Create remote directory if it doesn't exist
    log_info "Setting up remote directory..."
    ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_DIR}"

    # Sync files to VPS (excluding unnecessary files)
    log_info "Syncing files to VPS..."
    rsync -avz --delete \
        --exclude='venv/' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='.git/' \
        --exclude='.gitignore' \
        --exclude='.env' \
        --exclude='.env.local' \
        --exclude='*.log' \
        --exclude='uploads/' \
        --exclude='generated_pdfs/' \
        --exclude='test_*.py' \
        --exclude='*.md' \
        --exclude='.pytest_cache/' \
        --exclude='.coverage' \
        --exclude='htmlcov/' \
        --exclude='dist/' \
        --exclude='build/' \
        --exclude='*.egg-info/' \
        --exclude='.DS_Store' \
        --exclude='Thumbs.db' \
        ./ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/

    log_info "Files synced successfully"
}

# Setup Python environment on VPS
setup_python_env() {
    log_info "Setting up Python environment on VPS..."

    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
        set -e
        cd /home/docgen/backend

        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi

        # Activate venv and upgrade pip
        source venv/bin/activate
        pip install --upgrade pip wheel setuptools

        # Install dependencies
        echo "Installing dependencies..."
        pip install -r requirements-production.txt

        echo "Python environment setup complete"
EOF
}

# Setup environment file
setup_env_file() {
    log_info "Setting up environment file..."

    # Check if .env.production exists locally
    if [ ! -f ".env.production" ]; then
        log_error ".env.production not found locally"
        exit 1
    fi

    # Copy .env.production to VPS
    log_info "Copying .env.production to VPS..."
    scp .env.production ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/.env.production

    log_info "Environment file setup complete"
}

# Setup directories and permissions
setup_directories() {
    log_info "Setting up directories and permissions..."

    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
        set -e

        # Create necessary directories
        mkdir -p /home/docgen/uploads
        mkdir -p /home/docgen/generated_pdfs
        mkdir -p /var/log/docgen
        mkdir -p /var/run/docgen
        mkdir -p /tmp/docgen-uploads

        # Set permissions
        chmod 755 /home/docgen/uploads
        chmod 755 /home/docgen/generated_pdfs
        chmod 755 /var/log/docgen
        chmod 755 /var/run/docgen
        chmod 755 /tmp/docgen-uploads

        echo "Directories created and permissions set"
EOF
}

# Install and configure systemd service
setup_systemd() {
    log_info "Setting up systemd service..."

    # Copy service file to VPS
    scp docgen-backend.service ${REMOTE_USER}@${REMOTE_HOST}:/tmp/

    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
        set -e

        # Copy service file to systemd directory (requires sudo)
        sudo cp /tmp/docgen-backend.service /etc/systemd/system/

        # Reload systemd daemon
        sudo systemctl daemon-reload

        # Enable service to start on boot
        sudo systemctl enable docgen-backend.service

        echo "Systemd service configured"
EOF
}

# Configure Nginx
setup_nginx() {
    log_info "Setting up Nginx configuration..."

    # Copy nginx config to VPS
    scp nginx-production.conf ${REMOTE_USER}@${REMOTE_HOST}:/tmp/docgen-api

    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
        set -e

        # Copy nginx config (requires sudo)
        sudo cp /tmp/docgen-api /etc/nginx/sites-available/docgen-api

        # Create symlink if it doesn't exist
        if [ ! -L "/etc/nginx/sites-enabled/docgen-api" ]; then
            sudo ln -s /etc/nginx/sites-available/docgen-api /etc/nginx/sites-enabled/
        fi

        # Test nginx configuration
        sudo nginx -t

        echo "Nginx configuration installed"
EOF
}

# Restart services
restart_services() {
    log_info "Restarting services..."

    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
        set -e

        # Restart backend service
        sudo systemctl restart docgen-backend.service

        # Check service status
        sudo systemctl is-active docgen-backend.service

        # Reload nginx
        sudo systemctl reload nginx

        echo "Services restarted successfully"
EOF
}

# Run database migrations (if needed)
run_migrations() {
    log_info "Checking for database migrations..."

    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
        set -e
        cd /home/docgen/backend

        # Activate venv
        source venv/bin/activate

        # Run any migrations or database setup
        # python -m app.migrate (if you have migrations)

        echo "Migrations complete"
EOF
}

# Health check
health_check() {
    log_info "Running health check..."

    # Wait a few seconds for service to start
    sleep 5

    # Check if service is responding
    HEALTH_URL="https://${REMOTE_HOST}/health"

    if curl -f -s -o /dev/null -w "%{http_code}" $HEALTH_URL | grep -q "200"; then
        log_info "Health check passed! Backend is running."
    else
        log_error "Health check failed. Please check the service logs."

        # Show recent logs
        ssh ${REMOTE_USER}@${REMOTE_HOST} "sudo journalctl -u docgen-backend -n 50"
    fi
}

# Main deployment flow
main() {
    log_info "Starting DocGen Backend Deployment"
    log_info "Deploying to: ${REMOTE_USER}@${REMOTE_HOST}"

    # Confirmation
    read -p "Continue with deployment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi

    check_requirements
    check_git_status
    build_production
    deploy_to_vps
    setup_python_env
    setup_env_file
    setup_directories
    setup_systemd
    setup_nginx
    run_migrations
    restart_services
    health_check

    log_info "Deployment completed successfully!"
    log_info "Backend URL: https://${REMOTE_HOST}/api/v1/"
    log_info "Health endpoint: https://${REMOTE_HOST}/health"
}

# Parse arguments and run
parse_args "$@"

# Check if REMOTE_HOST is set
if [ "$REMOTE_HOST" = "your-vps-ip" ]; then
    log_error "Please specify VPS IP with --host option"
    exit 1
fi

# Run main deployment
main