#!/bin/bash

# Script to sync updated files from git repo to Docker backend directory
# Run this on VPS to update the backend with latest code

echo "=== Syncing Backend Files on VPS ==="

# Check if we're in the right place
if [ ! -d "/home/docgen/backend" ] || [ ! -d "/home/docgen/rapiddocs" ]; then
    echo "Error: Expected directories not found"
    echo "This script should be run on the VPS"
    exit 1
fi

echo "Updating git repository..."
cd /home/docgen/rapiddocs
git pull origin master

echo ""
echo "Backing up current backend files..."
cp -r /home/docgen/backend/app /home/docgen/backend/app.backup-$(date +%Y%m%d-%H%M%S)

echo ""
echo "Copying updated files from git repo to backend directory..."
# Copy the updated main_simple.py
cp /home/docgen/rapiddocs/backend/app/main_simple.py /home/docgen/backend/app/main_simple.py

# Copy other auth-related files
cp -r /home/docgen/rapiddocs/backend/app/routes /home/docgen/backend/app/
cp -r /home/docgen/rapiddocs/backend/app/services /home/docgen/backend/app/
cp -r /home/docgen/rapiddocs/backend/app/models /home/docgen/backend/app/
cp -r /home/docgen/rapiddocs/backend/app/middleware /home/docgen/backend/app/
cp -r /home/docgen/rapiddocs/backend/app/schemas /home/docgen/backend/app/
cp -r /home/docgen/rapiddocs/backend/app/templates /home/docgen/backend/app/

# Copy config if needed
cp /home/docgen/rapiddocs/backend/app/config.py /home/docgen/backend/app/config.py

echo ""
echo "Files synced. Now rebuilding Docker container..."
cd /home/docgen/backend

# Force rebuild without cache
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d

echo ""
echo "Waiting for container to be healthy..."
sleep 5

# Check container status
docker ps | grep rapiddocs

echo ""
echo "Testing CORS headers..."
echo ""
echo "From https://rapiddocs.io:"
curl -s -I -X OPTIONS https://api.rapiddocs.io/auth/login \
    -H "Origin: https://rapiddocs.io" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: content-type" \
    2>&1 | grep -E "Access-Control-Allow-Origin"

echo ""
echo "From https://rapiddocs-9a3f8.web.app:"
curl -s -I -X OPTIONS https://api.rapiddocs.io/auth/login \
    -H "Origin: https://rapiddocs-9a3f8.web.app" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: content-type" \
    2>&1 | grep -E "Access-Control-Allow-Origin"

echo ""
echo "Testing authentication endpoint..."
response=$(curl -s -X POST https://api.rapiddocs.io/auth/login \
    -H "Content-Type: application/json" \
    -H "Origin: https://rapiddocs.io" \
    -d '{"email":"test@rapiddocs.io","password":"testuser"}' \
    2>/dev/null)

if echo "$response" | grep -q "access_token"; then
    echo "✅ Authentication successful!"
else
    echo "❌ Authentication failed. Response:"
    echo "$response" | head -c 500
fi

echo ""
echo "Checking container logs..."
docker logs --tail=20 rapiddocs-backend

echo ""
echo "=== Sync Complete ==="
echo "The backend should now have the latest code with proper CORS configuration."