#!/bin/bash

# =============================================================================
# RapidDocs VPS - Fix Storage (Move to MongoDB GridFS)
# Downloads all files needed for GridFS-based storage
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
echo "RapidDocs - Fix Storage (GridFS Migration)"
echo "================================================"
echo ""
echo "This fix moves all file storage to MongoDB GridFS:"
echo "1. Logos stored in GridFS instead of filesystem"
echo "2. PDFs stored in GridFS instead of filesystem"
echo "3. No more permission errors on VPS"
echo ""

cd "$BACKEND_DIR"

# Stop containers
log_info "Stopping containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Create directories if needed
mkdir -p app/routes
mkdir -p app/services

# Download updated files from GitHub
log_info "Downloading updated files from GitHub..."

# Main application file
log_info "  - main_simple.py"
if ! wget -q -O app/main_simple.py "$REPO_RAW/app/main_simple.py"; then
    log_error "Failed to download main_simple.py"
    exit 1
fi

# PDF service with bytes generation
log_info "  - pdf_service.py"
if ! wget -q -O app/services/pdf_service.py "$REPO_RAW/app/services/pdf_service.py"; then
    log_error "Failed to download pdf_service.py"
    exit 1
fi

# New GridFS storage service
log_info "  - gridfs_storage.py (new)"
if ! wget -q -O app/services/gridfs_storage.py "$REPO_RAW/app/services/gridfs_storage.py"; then
    log_error "Failed to download gridfs_storage.py"
    exit 1
fi

# Auth routes fix
log_info "  - user_auth.py"
if ! wget -q -O app/routes/user_auth.py "$REPO_RAW/app/routes/user_auth.py"; then
    log_error "Failed to download user_auth.py"
    exit 1
fi

log_success "All files downloaded successfully"

# Rebuild and restart
log_info "Rebuilding containers (this may take a minute)..."
docker-compose build --no-cache 2>/dev/null || docker compose build --no-cache

log_info "Starting containers..."
docker-compose up -d 2>/dev/null || docker compose up -d

# Wait for container to start
log_info "Waiting for container to start..."
sleep 15

# Check status
log_info "Container status:"
docker-compose ps 2>/dev/null || docker compose ps

# Test the endpoint
echo ""
log_info "Testing health endpoint..."
if curl -s https://api.rapiddocs.io/health | grep -q "healthy"; then
    log_success "Health check passed!"
else
    log_warn "Health check may have failed - please verify manually"
fi

# Show recent logs
echo ""
log_info "Recent container logs:"
docker logs rapiddocs-backend --tail 20 2>/dev/null || docker-compose logs --tail 20 backend 2>/dev/null

echo ""
echo "================================================"
log_success "Storage fix applied successfully!"
echo "================================================"
echo ""
echo "Changes applied:"
echo "  - Files now stored in MongoDB GridFS"
echo "  - No filesystem access needed for documents"
echo "  - Fixed /auth/me to return real credits"
echo "  - Fixed /auth/refresh for JSON body"
echo ""
log_warn "IMPORTANT: Frontend also needs to be rebuilt and deployed!"
log_warn "Run locally: cd frontend && npm run build && firebase deploy --only hosting"
echo ""
