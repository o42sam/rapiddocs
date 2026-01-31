#!/bin/bash

# =============================================================================
# RapidDocs VPS Local Deployment Script
# Run this script DIRECTLY on the VPS (not from your local machine)
# =============================================================================

set -e

# Configuration
BACKEND_DIR="/home/docgen/backend"
BACKUP_DIR="/home/docgen/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "================================================"
echo "RapidDocs VPS Local Deployment Script"
echo "================================================"
echo ""

# Check if we're in the right directory or if backend exists
if [ ! -d "$BACKEND_DIR" ]; then
    log_error "Backend directory not found at $BACKEND_DIR"
    exit 1
fi

cd "$BACKEND_DIR"
log_info "Working directory: $(pwd)"

# Step 1: Create backup
echo ""
echo "Step 1: Creating backup..."
mkdir -p "$BACKUP_DIR"
if [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
    BACKUP_FILE="$BACKUP_DIR/backend_backup_$TIMESTAMP.tar.gz"
    tar -czf "$BACKUP_FILE" --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' --exclude='uploads/*' --exclude='generated/*' . 2>/dev/null || true
    log_success "Backup created: $BACKUP_FILE"
else
    log_warning "No docker-compose file found, skipping backup"
fi

# Step 2: Pull latest changes if git repo
echo ""
echo "Step 2: Checking for git updates..."
if [ -d ".git" ]; then
    log_info "Git repository detected"
    git fetch origin 2>/dev/null || log_warning "Could not fetch from origin"
    git status
    read -p "Pull latest changes? (y/N): " pull_changes
    if [[ "$pull_changes" =~ ^[Yy]$ ]]; then
        git pull origin $(git branch --show-current) || log_error "Git pull failed"
        log_success "Pulled latest changes"
    fi
else
    log_info "Not a git repository, skipping git pull"
fi

# Step 3: Check environment file
echo ""
echo "Step 3: Checking environment configuration..."
if [ -f ".env" ]; then
    log_success ".env file exists"
elif [ -f ".env.production" ]; then
    log_info "Copying .env.production to .env"
    cp .env.production .env
    log_success ".env file created from .env.production"
elif [ -f ".env.example" ]; then
    log_warning ".env file missing! .env.example exists"
    read -p "Copy .env.example to .env? (y/N): " copy_env
    if [[ "$copy_env" =~ ^[Yy]$ ]]; then
        cp .env.example .env
        log_warning "Please edit .env with your actual configuration!"
    fi
else
    log_error "No .env or .env.example file found!"
fi

# Step 4: Stop existing containers
echo ""
echo "Step 4: Stopping existing containers..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    log_error "Docker Compose not found!"
    exit 1
fi

$COMPOSE_CMD down --remove-orphans 2>/dev/null || log_warning "No containers to stop"
log_success "Containers stopped"

# Step 5: Rebuild containers
echo ""
echo "Step 5: Rebuilding Docker containers..."
$COMPOSE_CMD build --no-cache
log_success "Containers rebuilt"

# Step 6: Start containers
echo ""
echo "Step 6: Starting containers..."
$COMPOSE_CMD up -d
log_success "Containers started"

# Step 7: Wait for services to be ready
echo ""
echo "Step 7: Waiting for services to be ready..."
sleep 10

# Step 8: Health check
echo ""
echo "Step 8: Running health checks..."

# Check if containers are running
echo ""
log_info "Container status:"
$COMPOSE_CMD ps

# Try to hit the health endpoint
echo ""
log_info "Checking API health..."
for i in {1..5}; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q "200"; then
        log_success "API is healthy!"
        break
    elif curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null | grep -q "200\|404"; then
        log_success "API is responding!"
        break
    else
        if [ $i -eq 5 ]; then
            log_warning "API health check failed after 5 attempts"
            log_info "Checking container logs..."
            $COMPOSE_CMD logs --tail=50
        else
            log_info "Attempt $i/5 - waiting for API to start..."
            sleep 5
        fi
    fi
done

# Step 9: Show logs
echo ""
echo "Step 9: Recent logs..."
$COMPOSE_CMD logs --tail=20

echo ""
echo "================================================"
echo "Deployment Complete!"
echo "================================================"
echo ""
log_info "Useful commands:"
echo "  View logs:     $COMPOSE_CMD logs -f"
echo "  Stop:          $COMPOSE_CMD down"
echo "  Restart:       $COMPOSE_CMD restart"
echo "  Status:        $COMPOSE_CMD ps"
echo ""
log_info "Backup location: $BACKUP_DIR"
echo ""
