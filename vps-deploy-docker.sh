#!/bin/bash
# VPS Docker Deployment Script for RapidDocs
# This script deploys the backend using Docker on the VPS
#
# Usage:
#   - Directly on VPS: ./vps-deploy-docker.sh
#   - Download and run:
#     wget -O vps-deploy-docker.sh https://raw.githubusercontent.com/o42sam/rapiddocs/master/vps-deploy-docker.sh
#     chmod +x vps-deploy-docker.sh
#     ./vps-deploy-docker.sh

set -e

echo "=========================================="
echo "RapidDocs Docker Deployment Script"
echo "=========================================="

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

# Configuration
PROJECT_DIR="${VPS_PROJECT_DIR:-/home/docgen/rapiddocs}"
BACKEND_DIR="${PROJECT_DIR}/backend"
CONTAINER_NAME="rapiddocs-backend"

log_info "Project directory: $PROJECT_DIR"
log_info "Backend directory: $BACKEND_DIR"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    log_info "Docker installed successfully"
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    log_error "Docker Compose is not available."
    log_info "Installing Docker Compose plugin..."
    apt-get update && apt-get install -y docker-compose-plugin
fi

# Step 1: Pull latest code
log_info "Step 1: Pulling latest code from repository..."
cd "$PROJECT_DIR"

# Remove deployment scripts that might cause conflicts
rm -f vps-deploy-docker.sh vps-deploy-infographic.sh deploy-to-vps.sh 2>/dev/null || true

git pull

# Step 2: Setup environment file
log_info "Step 2: Setting up environment file..."
cd "$BACKEND_DIR"

if [ -f ".env.production" ]; then
    cp .env.production .env
    log_info "Copied .env.production to .env"
elif [ ! -f ".env" ]; then
    log_error ".env file not found and no .env.production to copy from!"
    log_error "Please create a .env file with the required configuration"
    exit 1
fi

# Step 3: Create necessary directories with proper permissions
log_info "Step 3: Creating necessary directories..."
mkdir -p uploads/logos generated_pdfs logs

# Fix permissions for mounted volumes (container runs as uid 1000)
chown -R 1000:1000 uploads generated_pdfs logs 2>/dev/null || true
chmod -R 755 uploads generated_pdfs logs

# Step 4: Stop existing container
log_info "Step 4: Stopping existing container (if any)..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

# Also stop any uvicorn processes running outside Docker
pkill -f 'uvicorn app.main:app' 2>/dev/null || true

# Step 5: Build Docker image
log_info "Step 5: Building Docker image..."
docker compose build --no-cache

# Step 6: Start container
log_info "Step 6: Starting Docker container..."
docker compose up -d

# Step 7: Wait for service to start
log_info "Step 7: Waiting for service to start..."
sleep 10

# Step 8: Verify deployment
log_info "Step 8: Verifying deployment..."

# Check container status
if docker ps | grep -q "$CONTAINER_NAME"; then
    log_info "Container is running"
else
    log_error "Container is not running!"
    log_error "Checking logs..."
    docker logs "$CONTAINER_NAME" --tail 50
    exit 1
fi

# Check health endpoint
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null || echo "failed")
if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    log_info "Health check passed: $HEALTH_RESPONSE"
else
    log_error "Health check failed: $HEALTH_RESPONSE"
    log_error "Container logs:"
    docker logs "$CONTAINER_NAME" --tail 100
    exit 1
fi

# Step 9: Check infographic endpoint
log_info "Step 9: Testing infographic endpoint..."
STATUS_RESPONSE=$(curl -s http://localhost:8000/api/v1/infographic/status 2>/dev/null || echo "failed")
echo "Infographic Status: $STATUS_RESPONSE"

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Container: $CONTAINER_NAME"
echo "Status: $(docker ps --filter name=$CONTAINER_NAME --format '{{.Status}}')"
echo ""
echo "Useful commands:"
echo "  View logs:     docker logs -f $CONTAINER_NAME"
echo "  Restart:       docker restart $CONTAINER_NAME"
echo "  Stop:          docker stop $CONTAINER_NAME"
echo "  Shell access:  docker exec -it $CONTAINER_NAME /bin/bash"
echo ""
echo "API Endpoints:"
echo "  Health:        http://localhost:8000/health"
echo "  Docs:          http://localhost:8000/api/v1/docs"
echo "  Infographic:   http://localhost:8000/api/v1/infographic/status"
echo ""
