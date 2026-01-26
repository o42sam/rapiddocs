#!/bin/bash

# RapidDocs Backend Deployment Script with Authentication
# This script deploys the updated backend with admin authentication

set -e

echo "================================================"
echo "RapidDocs Backend Deployment with Authentication"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root or with sudo${NC}"
   exit 1
fi

# VPS Configuration
BACKEND_DIR="/home/docgen/backend"
REPO_URL="https://github.com/o42sam/rapiddocs.git"

echo -e "${GREEN}Step 1: Creating backend directory...${NC}"
mkdir -p $BACKEND_DIR
cd $BACKEND_DIR

echo -e "${GREEN}Step 2: Pulling latest code from repository...${NC}"
if [ -d "rapiddocs" ]; then
    cd rapiddocs
    git pull origin master
    cd ..
else
    git clone $REPO_URL
fi

echo -e "${GREEN}Step 3: Copying backend files...${NC}"
cp -r rapiddocs/backend/* .

echo -e "${GREEN}Step 4: Checking .env.production file...${NC}"
if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}Warning: .env.production not found!${NC}"
    echo "Please create .env.production with your configuration"
    exit 1
fi

# Update JWT secrets if they haven't been set
if grep -q "GENERATE_NEW_KEY_WITH_python" .env.production; then
    echo -e "${YELLOW}Generating JWT secret keys...${NC}"
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    JWT_REFRESH_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

    sed -i "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$JWT_SECRET|" .env.production
    sed -i "s|JWT_REFRESH_SECRET_KEY=.*|JWT_REFRESH_SECRET_KEY=$JWT_REFRESH_SECRET|" .env.production

    echo -e "${GREEN}JWT secrets generated and updated${NC}"
fi

echo -e "${GREEN}Step 5: Stopping existing containers...${NC}"
docker-compose down || true

echo -e "${GREEN}Step 6: Building Docker image...${NC}"
docker-compose build --no-cache

echo -e "${GREEN}Step 7: Starting containers...${NC}"
docker-compose up -d

echo -e "${GREEN}Step 8: Waiting for services to start...${NC}"
sleep 10

echo -e "${GREEN}Step 9: Checking container status...${NC}"
docker ps | grep rapiddocs-backend

echo -e "${GREEN}Step 10: Checking application logs...${NC}"
docker-compose logs --tail=50

echo -e "${GREEN}Step 11: Testing health endpoint...${NC}"
curl -s http://localhost:8000/health || echo -e "${RED}Health check failed${NC}"

echo -e "${GREEN}Step 12: Checking for initial referral key...${NC}"
echo "================================================"
echo "IMPORTANT: Check the logs above for the initial referral key"
echo "Look for 'INITIAL SETUP - SAVE THIS INFORMATION!'"
echo "Use this key to register the first admin at https://api.rapiddocs.io/register"
echo "================================================"

# Save the initial referral key if shown in logs
docker-compose logs | grep -A 3 "INITIAL SETUP" > initial_key.txt 2>/dev/null || true

if [ -s initial_key.txt ]; then
    echo -e "${YELLOW}Initial referral key saved to: $BACKEND_DIR/initial_key.txt${NC}"
    cat initial_key.txt
fi

echo ""
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Access https://api.rapiddocs.io to see the login page"
echo "2. Use the initial referral key to register the first admin at https://api.rapiddocs.io/register"
echo "3. After registration, login at https://api.rapiddocs.io/login"
echo "4. Access the admin dashboard at https://api.rapiddocs.io/admin/dashboard"
echo ""
echo "API Documentation: https://api.rapiddocs.io/docs"
echo "Health Check: https://api.rapiddocs.io/health (requires auth)"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To restart: docker-compose restart"
echo "To stop: docker-compose down"