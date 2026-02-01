#!/bin/bash

# =============================================================================
# RapidDocs VPS - Fix Credits Display & Auth
# Downloads fixed files that return real credits from database
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
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "================================================"
echo "RapidDocs - Fix Credits Display & Auth"
echo "================================================"
echo ""
echo "This fix:"
echo "1. Updates /auth/me to return real credits from DB"
echo "2. Fixes /auth/refresh to accept JSON body"
echo "3. Fixes auth response format for frontend"
echo ""

cd "$BACKEND_DIR"

# Stop containers
log_info "Stopping containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Create directories if needed
mkdir -p app/routes

# Download the fixed user_auth.py from GitHub
log_info "Downloading fixed user_auth.py from GitHub..."
if wget -O app/routes/user_auth.py "$REPO_RAW/app/routes/user_auth.py"; then
    log_success "Downloaded user_auth.py successfully"
else
    log_error "Failed to download user_auth.py"
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
log_success "Backend fix applied successfully!"
echo "================================================"
echo ""
log_warn "IMPORTANT: Frontend also needs to be rebuilt and deployed!"
log_warn "The frontend fix is already pushed to GitHub."
log_warn ""
log_warn "If using Firebase Hosting, run locally:"
log_warn "  cd frontend && npm run build"
log_warn "  firebase deploy --only hosting"
log_warn ""
log_warn "After frontend deployment, users should:"
log_warn "1. Clear browser localStorage (or logout)"
log_warn "2. Log back in to see correct credits"
echo ""
