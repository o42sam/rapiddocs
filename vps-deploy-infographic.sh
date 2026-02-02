#!/bin/bash
# VPS Deployment Script for Infographic Generation
# This script updates the RapidDocs backend with infographic generation support

set -e

echo "=========================================="
echo "RapidDocs Infographic Deployment Script"
echo "=========================================="

# Configuration - Update these for your VPS
VPS_USER="${VPS_USER:-root}"
VPS_HOST="${VPS_HOST:-your-vps-ip}"
VPS_PROJECT_DIR="${VPS_PROJECT_DIR:-/var/www/rapiddocs}"
VPS_BACKEND_DIR="${VPS_PROJECT_DIR}/backend"
SERVICE_NAME="${SERVICE_NAME:-rapiddocs}"

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

# Check if VPS_HOST is configured
if [ "$VPS_HOST" = "your-vps-ip" ]; then
    log_error "Please configure VPS_HOST before running this script"
    echo ""
    echo "Usage: VPS_HOST=192.168.1.100 ./vps-deploy-infographic.sh"
    echo "Or edit the script to set VPS_HOST directly"
    exit 1
fi

log_info "Deploying to $VPS_USER@$VPS_HOST:$VPS_PROJECT_DIR"

# Step 1: Pull latest changes on VPS
log_info "Step 1: Pulling latest code from repository..."
ssh $VPS_USER@$VPS_HOST "cd $VPS_PROJECT_DIR && git pull"

# Step 2: Install new Python dependencies
log_info "Step 2: Installing Python dependencies..."
ssh $VPS_USER@$VPS_HOST "cd $VPS_BACKEND_DIR && pip install -r requirements.txt"

# Step 3: Create necessary directories
log_info "Step 3: Creating necessary directories..."
ssh $VPS_USER@$VPS_HOST "mkdir -p $VPS_BACKEND_DIR/generated_pdfs"
ssh $VPS_USER@$VPS_HOST "mkdir -p $VPS_BACKEND_DIR/uploads/logos"

# Step 4: Restart the backend service
log_info "Step 4: Restarting the backend service..."
if ssh $VPS_USER@$VPS_HOST "systemctl is-active --quiet $SERVICE_NAME"; then
    ssh $VPS_USER@$VPS_HOST "sudo systemctl restart $SERVICE_NAME"
    log_info "Service $SERVICE_NAME restarted"
else
    log_warn "Service $SERVICE_NAME not found, trying with uvicorn directly..."
    # Kill any existing uvicorn process
    ssh $VPS_USER@$VPS_HOST "pkill -f 'uvicorn app.main:app' || true"
    # Start in background
    ssh $VPS_USER@$VPS_HOST "cd $VPS_BACKEND_DIR && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /var/log/rapiddocs.log 2>&1 &"
    log_info "Started uvicorn server"
fi

# Step 5: Wait for service to start
log_info "Step 5: Waiting for service to start..."
sleep 5

# Step 6: Verify deployment
log_info "Step 6: Verifying deployment..."

# Check health endpoint
HEALTH_RESPONSE=$(ssh $VPS_USER@$VPS_HOST "curl -s http://localhost:8000/health" 2>/dev/null || echo "failed")
if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    log_info "Health check passed: $HEALTH_RESPONSE"
else
    log_error "Health check failed: $HEALTH_RESPONSE"
    exit 1
fi

# Check component status endpoint
log_info "Checking infographic component status..."
STATUS_RESPONSE=$(ssh $VPS_USER@$VPS_HOST "curl -s http://localhost:8000/api/v1/infographic/status" 2>/dev/null || echo "failed")
echo "Component Status:"
echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"

# Step 7: Test infographic generation endpoint
log_info "Step 7: Testing infographic generation endpoint..."
TEST_RESPONSE=$(ssh $VPS_USER@$VPS_HOST "curl -s -X POST 'http://localhost:8000/api/v1/generate/document' \
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
echo "To set environment variables on VPS:"
echo "  ssh $VPS_USER@$VPS_HOST"
echo "  export GEMINI_API_KEY=your_key_here"
echo "  export HUGGINGFACE_API_KEY=your_key_here"
echo "  sudo systemctl restart $SERVICE_NAME"
