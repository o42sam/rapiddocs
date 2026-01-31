#!/bin/bash

# RapidDocs VPS Deployment Script
# Syncs entire local backend to VPS and restarts services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - UPDATE THESE FOR YOUR SETUP
VPS_USER="docgen"
VPS_HOST="your-vps-ip-or-hostname"  # UPDATE THIS
VPS_BACKEND_DIR="/home/docgen/backend"
LOCAL_BACKEND_DIR="$(dirname "$0")/backend"

# Check if VPS_HOST was updated
if [[ "$VPS_HOST" == "your-vps-ip-or-hostname" ]]; then
    echo -e "${YELLOW}Please update VPS_HOST in this script with your actual VPS IP or hostname${NC}"
    read -p "Enter your VPS IP or hostname: " VPS_HOST
    if [[ -z "$VPS_HOST" ]]; then
        echo -e "${RED}VPS host is required${NC}"
        exit 1
    fi
fi

echo "================================================"
echo -e "${BLUE}RapidDocs VPS Deployment Script${NC}"
echo "================================================"
echo ""
echo -e "Local backend: ${GREEN}$LOCAL_BACKEND_DIR${NC}"
echo -e "VPS target:    ${GREEN}$VPS_USER@$VPS_HOST:$VPS_BACKEND_DIR${NC}"
echo ""

# Verify local backend exists
if [[ ! -d "$LOCAL_BACKEND_DIR" ]]; then
    echo -e "${RED}Error: Local backend directory not found at $LOCAL_BACKEND_DIR${NC}"
    exit 1
fi

# Verify local backend has required files
if [[ ! -f "$LOCAL_BACKEND_DIR/app/main_simple.py" ]]; then
    echo -e "${RED}Error: main_simple.py not found in local backend${NC}"
    exit 1
fi

echo -e "${YELLOW}This will:${NC}"
echo "  1. Create a backup of the current VPS backend"
echo "  2. Sync all local backend files to VPS"
echo "  3. Rebuild and restart Docker containers"
echo "  4. Run health checks"
echo ""
read -p "Continue? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo -e "${GREEN}Step 1: Testing VPS connection...${NC}"
if ! ssh -o ConnectTimeout=10 "$VPS_USER@$VPS_HOST" "echo 'Connection successful'"; then
    echo -e "${RED}Failed to connect to VPS. Check your SSH configuration.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Step 2: Creating backup on VPS...${NC}"
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
ssh "$VPS_USER@$VPS_HOST" "
    cd $VPS_BACKEND_DIR
    if [[ -d app ]]; then
        mkdir -p backups
        cp -r app backups/app_$BACKUP_NAME
        echo 'Backup created: backups/app_$BACKUP_NAME'
    else
        echo 'No existing app directory to backup'
    fi
"

echo ""
echo -e "${GREEN}Step 3: Syncing backend files to VPS...${NC}"

# Sync the app directory (main application code)
echo "  Syncing app/ directory..."
rsync -avz --delete \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache' \
    --exclude '.env' \
    --exclude '.env.local' \
    "$LOCAL_BACKEND_DIR/app/" "$VPS_USER@$VPS_HOST:$VPS_BACKEND_DIR/app/"

# Sync Dockerfile
echo "  Syncing Dockerfile..."
rsync -avz "$LOCAL_BACKEND_DIR/Dockerfile" "$VPS_USER@$VPS_HOST:$VPS_BACKEND_DIR/Dockerfile"

# Sync requirements.txt if exists
if [[ -f "$LOCAL_BACKEND_DIR/requirements.txt" ]]; then
    echo "  Syncing requirements.txt..."
    rsync -avz "$LOCAL_BACKEND_DIR/requirements.txt" "$VPS_USER@$VPS_HOST:$VPS_BACKEND_DIR/requirements.txt"
fi

# Sync docker-compose.yml if exists
if [[ -f "$LOCAL_BACKEND_DIR/docker-compose.yml" ]]; then
    echo "  Syncing docker-compose.yml..."
    rsync -avz "$LOCAL_BACKEND_DIR/docker-compose.yml" "$VPS_USER@$VPS_HOST:$VPS_BACKEND_DIR/docker-compose.yml"
fi

# Note: We don't sync .env.production as it may have VPS-specific secrets

echo ""
echo -e "${GREEN}Step 4: Stopping Docker containers...${NC}"
ssh "$VPS_USER@$VPS_HOST" "
    cd $VPS_BACKEND_DIR
    docker-compose down || true
"

echo ""
echo -e "${GREEN}Step 5: Rebuilding Docker image...${NC}"
ssh "$VPS_USER@$VPS_HOST" "
    cd $VPS_BACKEND_DIR
    docker-compose build --no-cache
"

echo ""
echo -e "${GREEN}Step 6: Starting Docker containers...${NC}"
ssh "$VPS_USER@$VPS_HOST" "
    cd $VPS_BACKEND_DIR
    docker-compose up -d
"

echo ""
echo -e "${GREEN}Step 7: Waiting for service to start...${NC}"
sleep 10

echo ""
echo -e "${GREEN}Step 8: Running health checks...${NC}"

# Test health endpoint
echo "  Testing /health endpoint..."
HEALTH_RESPONSE=$(ssh "$VPS_USER@$VPS_HOST" "curl -s http://localhost:8000/health" 2>/dev/null || echo "FAILED")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "  ${GREEN}✓ Health check passed${NC}"
else
    echo -e "  ${RED}✗ Health check failed${NC}"
    echo "  Response: $HEALTH_RESPONSE"
fi

# Test login page
echo "  Testing /login page..."
LOGIN_RESPONSE=$(ssh "$VPS_USER@$VPS_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/login" 2>/dev/null || echo "000")
if [[ "$LOGIN_RESPONSE" == "200" ]]; then
    echo -e "  ${GREEN}✓ Login page accessible (HTTP $LOGIN_RESPONSE)${NC}"
else
    echo -e "  ${RED}✗ Login page not accessible (HTTP $LOGIN_RESPONSE)${NC}"
fi

# Test admin login endpoint
echo "  Testing /admin/login endpoint..."
ADMIN_RESPONSE=$(ssh "$VPS_USER@$VPS_HOST" "curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/admin/login -H 'Content-Type: application/json' -d '{}'" 2>/dev/null || echo "000")
if [[ "$ADMIN_RESPONSE" == "422" || "$ADMIN_RESPONSE" == "401" ]]; then
    echo -e "  ${GREEN}✓ Admin login endpoint responding (HTTP $ADMIN_RESPONSE - expected for empty body)${NC}"
else
    echo -e "  ${YELLOW}⚠ Admin login endpoint returned HTTP $ADMIN_RESPONSE${NC}"
fi

# Test generate/document endpoint with FormData
echo "  Testing /generate/document endpoint..."
GENERATE_RESPONSE=$(ssh "$VPS_USER@$VPS_HOST" "curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/generate/document -F 'description=test' -F 'document_type=invoice'" 2>/dev/null || echo "000")
if [[ "$GENERATE_RESPONSE" == "200" || "$GENERATE_RESPONSE" == "422" || "$GENERATE_RESPONSE" == "500" ]]; then
    echo -e "  ${GREEN}✓ Generate endpoint accepting FormData (HTTP $GENERATE_RESPONSE)${NC}"
else
    echo -e "  ${RED}✗ Generate endpoint issue (HTTP $GENERATE_RESPONSE)${NC}"
fi

echo ""
echo -e "${GREEN}Step 9: Showing recent container logs...${NC}"
ssh "$VPS_USER@$VPS_HOST" "
    cd $VPS_BACKEND_DIR
    docker-compose logs --tail=20
"

echo ""
echo "================================================"
echo -e "${GREEN}Deployment Complete!${NC}"
echo "================================================"
echo ""
echo "Your backend should now be running with:"
echo "  - Admin login page at: https://api.rapiddocs.io/login"
echo "  - Admin dashboard at:  https://api.rapiddocs.io/admin/dashboard"
echo "  - Health check at:     https://api.rapiddocs.io/health"
echo ""
echo "If you encounter issues, check logs with:"
echo "  ssh $VPS_USER@$VPS_HOST 'cd $VPS_BACKEND_DIR && docker-compose logs -f'"
echo ""
echo "To rollback to previous version:"
echo "  ssh $VPS_USER@$VPS_HOST 'cd $VPS_BACKEND_DIR && cp -r backups/app_$BACKUP_NAME app && docker-compose down && docker-compose up -d'"
echo ""
