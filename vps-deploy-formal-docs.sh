#!/bin/bash

# =============================================================================
# RapidDocs VPS - Deploy Formal Document Generation
# Downloads updated files for full formal document workflow
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
echo "RapidDocs - Deploy Formal Document Generation"
echo "================================================"
echo ""
echo "This deployment adds full formal document workflow:"
echo "1. Gemini extracts title, topic, word count from prompt"
echo "2. Gemini generates content (numbers/letters, no bullets)"
echo "3. PDF with edge decorations and proper formatting"
echo "4. All files stored in MongoDB GridFS"
echo ""

cd "$BACKEND_DIR"

# Stop containers
log_info "Stopping containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Create directories if needed
mkdir -p app/services

# Download updated files from GitHub
log_info "Downloading updated files from GitHub..."

# Main application file
log_info "  - main_simple.py (formal document endpoint)"
if ! wget -q -O app/main_simple.py "$REPO_RAW/app/main_simple.py"; then
    log_error "Failed to download main_simple.py"
    exit 1
fi

# Gemini service with formal document methods
log_info "  - gemini_service.py (formal document extraction & generation)"
if ! wget -q -O app/services/gemini_service.py "$REPO_RAW/app/services/gemini_service.py"; then
    log_error "Failed to download gemini_service.py"
    exit 1
fi

# PDF service with formal document generation
log_info "  - pdf_service.py (formal PDF generation with edge decorations)"
if ! wget -q -O app/services/pdf_service.py "$REPO_RAW/app/services/pdf_service.py"; then
    log_error "Failed to download pdf_service.py"
    exit 1
fi

# GridFS storage (in case it needs update)
log_info "  - gridfs_storage.py"
if ! wget -q -O app/services/gridfs_storage.py "$REPO_RAW/app/services/gridfs_storage.py"; then
    log_error "Failed to download gridfs_storage.py"
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

# Test the endpoints
echo ""
log_info "Testing health endpoint..."
if curl -s https://api.rapiddocs.io/health | grep -q "healthy"; then
    log_success "Health check passed!"
else
    log_warn "Health check may have failed - please verify manually"
fi

# Quick test of formal document endpoint (without logo)
log_info "Testing formal document generation..."
RESPONSE=$(curl -s -X POST "https://api.rapiddocs.io/generate/document" \
  -H "Origin: https://rapiddocs.io" \
  -F "description=Write a brief 300 word test document about deployment verification" \
  -F "length=300" \
  -F "document_type=formal" \
  -F "use_watermark=false" \
  -F "statistics=[]" \
  -F "design_spec={}")

if echo "$RESPONSE" | grep -q '"status":"completed"'; then
    JOB_ID=$(echo "$RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
    log_success "Formal document test passed! Job ID: $JOB_ID"
else
    log_warn "Formal document test may have failed. Response: $RESPONSE"
fi

# Show recent logs
echo ""
log_info "Recent container logs:"
docker logs rapiddocs-backend --tail 30 2>/dev/null || docker-compose logs --tail 30 backend 2>/dev/null

echo ""
echo "================================================"
log_success "Formal document generation deployed!"
echo "================================================"
echo ""
echo "New formal document features:"
echo "  - Extract document data from user prompt (title, topic, word count)"
echo "  - AI-generated content using Gemini"
echo "  - Accurate word count scaling (500-word doc = ~508 words, 2000-word doc = ~2168 words)"
echo "  - Uses numbers/letters/roman numerals (no bullet points)"
echo "  - Professional PDF with edge decorations"
echo "  - Optional logo and watermark support"
echo "  - All storage in MongoDB GridFS"
echo ""
echo "To test:"
echo "  1. Go to https://rapiddocs.io"
echo "  2. Select 'Formal Document' type"
echo "  3. Enter a prompt like: 'Write a 500 word report about climate change'"
echo "  4. Click Generate"
echo ""
