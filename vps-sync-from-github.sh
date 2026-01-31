#!/bin/bash

# =============================================================================
# RapidDocs VPS Sync from GitHub
# Downloads the correct files from the GitHub repo
# =============================================================================

set -e

BACKEND_DIR="/home/docgen/backend"
REPO_RAW="https://raw.githubusercontent.com/o42sam/rapiddocs/master/backend"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

echo "================================================"
echo "RapidDocs - Sync from GitHub"
echo "================================================"

cd "$BACKEND_DIR"

# Stop containers
log_info "Stopping containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Create directories
mkdir -p app/templates

# Download templates from GitHub
log_info "Downloading templates from GitHub..."
wget -O app/templates/login.html "$REPO_RAW/app/templates/login.html"
wget -O app/templates/register.html "$REPO_RAW/app/templates/register.html"
wget -O app/templates/dashboard.html "$REPO_RAW/app/templates/dashboard.html"

# Download the correct main_simple.py
log_info "Downloading main_simple.py from GitHub..."
wget -O app/main_simple.py "$REPO_RAW/app/main_simple.py"

log_success "Files downloaded"

# Rebuild and restart
log_info "Rebuilding containers..."
docker-compose build --no-cache 2>/dev/null || docker compose build --no-cache

log_info "Starting containers..."
docker-compose up -d 2>/dev/null || docker compose up -d

sleep 10

log_info "Container status:"
docker-compose ps 2>/dev/null || docker compose ps

echo ""
log_success "Sync complete! Test https://api.rapiddocs.io/"
