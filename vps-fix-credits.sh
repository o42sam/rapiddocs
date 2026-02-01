#!/bin/bash

# =============================================================================
# RapidDocs VPS - Fix Credits Display
# Downloads the fixed user_auth.py that returns real credits from database
# =============================================================================

set -e

BACKEND_DIR="/home/docgen/backend"
REPO_RAW="https://raw.githubusercontent.com/o42sam/rapiddocs/master/backend"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

echo "================================================"
echo "RapidDocs - Fix Credits Display"
echo "================================================"
echo ""
echo "This fix updates /auth/me endpoint to return"
echo "actual user credits from database instead of"
echo "hardcoded value (100)."
echo ""

cd "$BACKEND_DIR"

# Stop containers
log_info "Stopping containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Create directories if needed
mkdir -p app/routes

# Download the fixed user_auth.py from GitHub
log_info "Downloading fixed user_auth.py from GitHub..."
wget -O app/routes/user_auth.py "$REPO_RAW/app/routes/user_auth.py"

if [ $? -eq 0 ]; then
    log_success "Downloaded user_auth.py successfully"
else
    echo -e "${RED}[ERROR]${NC} Failed to download user_auth.py"
    exit 1
fi

# Rebuild and restart
log_info "Rebuilding containers..."
docker-compose build --no-cache 2>/dev/null || docker compose build --no-cache

log_info "Starting containers..."
docker-compose up -d 2>/dev/null || docker compose up -d

# Wait for container to start
log_info "Waiting for container to start..."
sleep 10

# Check status
log_info "Container status:"
docker-compose ps 2>/dev/null || docker compose ps

# Test the endpoint
echo ""
log_info "Testing health endpoint..."
curl -s https://api.rapiddocs.io/health || echo "Health check failed"

echo ""
echo "================================================"
log_success "Fix applied successfully!"
echo "================================================"
echo ""
log_warn "Users need to log out and log back in to see"
log_warn "correct credits, or clear browser localStorage."
echo ""
