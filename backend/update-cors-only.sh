#!/bin/bash

# Simple CORS update script for VPS
# Run this on the VPS as root in /root/rapiddocs-backend

echo "=== Updating CORS Configuration ==="

# Check if we're in the right directory
if [ ! -f ".env.production" ]; then
    echo "Error: .env.production not found. Are you in /root/rapiddocs-backend?"
    exit 1
fi

# Backup the existing file
cp .env.production .env.production.cors-backup

# Update only the CORS_ORIGINS line
sed -i 's|^CORS_ORIGINS=.*|CORS_ORIGINS=https://rapiddocs.io,https://www.rapiddocs.io,https://rapiddocs-9a3f8.web.app,https://rapiddocs.web.app,https://rapiddocs.firebaseapp.com,http://localhost:3000,http://localhost:5173|' .env.production

echo "Updated CORS_ORIGINS in .env.production"

# Restart the container
echo "Restarting Docker container..."
docker-compose down
docker-compose up -d

# Wait for container to be healthy
echo "Waiting for container to be healthy..."
for i in {1..30}; do
    if docker ps | grep -q "healthy"; then
        echo "Container is healthy!"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "Testing CORS headers..."
echo ""
echo "From rapiddocs.io:"
curl -s -I -X OPTIONS https://api.rapiddocs.io/auth/login \
    -H "Origin: https://rapiddocs.io" \
    -H "Access-Control-Request-Method: POST" \
    2>&1 | grep -E "Access-Control-Allow-Origin"

echo ""
echo "From rapiddocs-9a3f8.web.app:"
curl -s -I -X OPTIONS https://api.rapiddocs.io/auth/login \
    -H "Origin: https://rapiddocs-9a3f8.web.app" \
    -H "Access-Control-Request-Method: POST" \
    2>&1 | grep -E "Access-Control-Allow-Origin"

echo ""
echo "=== CORS Update Complete ==="
echo ""
echo "The backend now accepts requests from:"
echo "  ✅ https://rapiddocs.io"
echo "  ✅ https://www.rapiddocs.io"
echo "  ✅ https://rapiddocs-9a3f8.web.app"
echo ""
echo "Try logging in from https://rapiddocs.io with:"
echo "  Email: test@rapiddocs.io"
echo "  Password: testuser"