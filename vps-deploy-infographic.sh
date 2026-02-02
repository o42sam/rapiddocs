#!/bin/bash
# VPS Deployment Script for Infographic Generation
# This script updates the RapidDocs backend with infographic generation support
#
# Can be run:
#   - Directly on VPS: ./vps-deploy-infographic.sh
#   - Remotely via SSH: VPS_HOST=192.168.1.100 ./vps-deploy-infographic.sh

set -e

echo "=========================================="
echo "RapidDocs Infographic Deployment Script"
echo "=========================================="

# Configuration
VPS_USER="${VPS_USER:-root}"
VPS_HOST="${VPS_HOST:-local}"
SERVICE_NAME="${SERVICE_NAME:-rapiddocs}"

# Auto-detect project directory (must have .git)
if [ -d "/home/docgen/rapiddocs/.git" ]; then
    DEFAULT_PROJECT_DIR="/home/docgen/rapiddocs"
elif [ -d "/home/docgen/.git" ]; then
    DEFAULT_PROJECT_DIR="/home/docgen"
elif [ -d "/var/www/rapiddocs/.git" ]; then
    DEFAULT_PROJECT_DIR="/var/www/rapiddocs"
elif [ -d ".git" ]; then
    DEFAULT_PROJECT_DIR="$(pwd)"
else
    DEFAULT_PROJECT_DIR="$(pwd)"
fi

PROJECT_DIR="${VPS_PROJECT_DIR:-$DEFAULT_PROJECT_DIR}"
BACKEND_DIR="${PROJECT_DIR}/backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Determine if running locally or remotely
if [ "$VPS_HOST" = "local" ] || [ "$VPS_HOST" = "localhost" ] || [ "$VPS_HOST" = "127.0.0.1" ]; then
    LOCAL_MODE=true
    log_info "Running in LOCAL mode on this server"
    log_info "Project directory: $PROJECT_DIR"

    # Function to run commands locally
    run_cmd() {
        eval "$1"
    }
else
    LOCAL_MODE=false
    log_info "Running in REMOTE mode via SSH to $VPS_USER@$VPS_HOST"
    log_info "Project directory: $PROJECT_DIR"

    # Function to run commands via SSH
    run_cmd() {
        ssh $VPS_USER@$VPS_HOST "$1"
    }
fi

# Step 1: Pull latest changes
log_info "Step 1: Pulling latest code from repository..."

# Remove deployment scripts from repo directory if they exist as untracked (prevents merge conflict)
# The script is downloaded separately to the parent directory, so the repo copy is redundant
run_cmd "cd $PROJECT_DIR && rm -f vps-deploy-infographic.sh deploy-to-vps.sh 2>/dev/null || true"

run_cmd "cd $PROJECT_DIR && git pull"

# Step 2: Install new Python dependencies
log_info "Step 2: Installing Python dependencies..."
run_cmd "cd $BACKEND_DIR && pip install -r requirements.txt"

# Step 3: Create necessary directories
log_info "Step 3: Creating necessary directories..."
run_cmd "mkdir -p $BACKEND_DIR/generated_pdfs"
run_cmd "mkdir -p $BACKEND_DIR/uploads/logos"

# Step 4: Restart the backend service
log_info "Step 4: Restarting the backend service..."

# Check if systemd service exists
if run_cmd "systemctl is-active --quiet $SERVICE_NAME 2>/dev/null"; then
    run_cmd "systemctl restart $SERVICE_NAME"
    log_info "Service $SERVICE_NAME restarted"
else
    log_warn "Service $SERVICE_NAME not found, trying with uvicorn directly..."
    # Kill any existing uvicorn process
    run_cmd "pkill -f 'uvicorn app.main:app' || true"
    sleep 2
    # Start in background
    if [ "$LOCAL_MODE" = true ]; then
        cd $BACKEND_DIR
        nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /var/log/rapiddocs.log 2>&1 &
        cd - > /dev/null
    else
        run_cmd "cd $BACKEND_DIR && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /var/log/rapiddocs.log 2>&1 &"
    fi
    log_info "Started uvicorn server"
fi

# Step 5: Wait for service to start
log_info "Step 5: Waiting for service to start..."
sleep 5

# Step 6: Verify deployment
log_info "Step 6: Verifying deployment..."

# Check health endpoint
HEALTH_RESPONSE=$(run_cmd "curl -s http://localhost:8000/health" 2>/dev/null || echo "failed")
if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    log_info "Health check passed: $HEALTH_RESPONSE"
else
    log_error "Health check failed: $HEALTH_RESPONSE"
    log_warn "Check logs at /var/log/rapiddocs.log"
    exit 1
fi

# Check component status endpoint
log_info "Checking infographic component status..."
STATUS_RESPONSE=$(run_cmd "curl -s http://localhost:8000/api/v1/infographic/status" 2>/dev/null || echo "failed")
echo "Component Status:"
echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"

# Step 7: Test infographic generation endpoint
log_info "Step 7: Testing infographic generation endpoint..."
TEST_RESPONSE=$(run_cmd "curl -s -X POST 'http://localhost:8000/api/v1/generate/document' \
    -F 'description=Test infographic about technology trends' \
    -F 'length=300' \
    -F 'document_type=infographic' \
    -F 'use_watermark=false' \
    -F 'statistics=[]' \
    -F 'design_spec={}'" 2>/dev/null || echo "failed")

if [[ "$TEST_RESPONSE" == *"job_id"* ]] && [[ "$TEST_RESPONSE" == *"completed"* ]]; then
    log_info "Test generation successful!"
    echo "Response: $TEST_RESPONSE"
else
    log_warn "Test generation response: $TEST_RESPONSE"
    log_warn "This may be normal if AI APIs are rate-limited"
fi

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Infographic Generation Endpoints:"
echo "  POST /api/v1/generate/document     - Unified document generation"
echo "  POST /api/v1/infographic/generate  - Direct infographic generation"
echo "  GET  /api/v1/infographic/status    - Component status"
echo "  GET  /api/v1/generate/status/{id}  - Job status"
echo "  GET  /api/v1/generate/download/{id} - Download PDF"
echo ""
echo "Required Environment Variables:"
echo "  GEMINI_API_KEY       - Google Gemini API key (for text generation)"
echo "  HUGGINGFACE_API_KEY  - HuggingFace API key (for image generation)"
echo ""
echo "To set environment variables, add to /etc/environment or .env file:"
echo "  GEMINI_API_KEY=your_key_here"
echo "  HUGGINGFACE_API_KEY=your_key_here"
