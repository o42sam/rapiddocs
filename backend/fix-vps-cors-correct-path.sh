#!/bin/bash

# CORS fix for actual VPS setup at /home/docgen/backend
# Run this on the VPS as root

echo "=== Fixing CORS Configuration on VPS ==="
echo "Working directory: /home/docgen/backend"

cd /home/docgen/backend

# Check if we're in the right directory
if [ ! -f ".env.production" ]; then
    echo "Error: .env.production not found in /home/docgen/backend"
    exit 1
fi

echo ""
echo "Current CORS setting:"
grep "^CORS_ORIGINS=" .env.production || echo "CORS_ORIGINS not found!"

# Backup the existing file
cp .env.production .env.production.backup-$(date +%Y%m%d-%H%M%S)

# Update the CORS_ORIGINS line
echo ""
echo "Updating CORS_ORIGINS..."

# First check if CORS_ORIGINS exists
if grep -q "^CORS_ORIGINS=" .env.production; then
    # Update existing line
    sed -i 's|^CORS_ORIGINS=.*|CORS_ORIGINS=https://rapiddocs.io,https://www.rapiddocs.io,https://rapiddocs-9a3f8.web.app,https://rapiddocs.web.app,https://rapiddocs.firebaseapp.com|' .env.production
    echo "Updated existing CORS_ORIGINS line"
else
    # Add CORS_ORIGINS if it doesn't exist
    echo "" >> .env.production
    echo "# CORS Configuration" >> .env.production
    echo "CORS_ORIGINS=https://rapiddocs.io,https://www.rapiddocs.io,https://rapiddocs-9a3f8.web.app,https://rapiddocs.web.app,https://rapiddocs.firebaseapp.com" >> .env.production
    echo "Added CORS_ORIGINS line"
fi

echo ""
echo "New CORS setting:"
grep "^CORS_ORIGINS=" .env.production

# Check if docker-compose.yml exists in current directory
if [ ! -f "docker-compose.yml" ]; then
    echo ""
    echo "Warning: docker-compose.yml not found in /home/docgen/backend"
    echo "Looking for Docker container..."

    # Find the running container
    CONTAINER_NAME=$(docker ps --format "table {{.Names}}" | grep -i rapid | head -1)

    if [ -z "$CONTAINER_NAME" ]; then
        echo "Error: No RapidDocs container found running"
        docker ps
        exit 1
    fi

    echo "Found container: $CONTAINER_NAME"
    echo "Restarting container..."
    docker restart $CONTAINER_NAME
else
    # Use docker-compose if available
    echo ""
    echo "Restarting Docker container with docker-compose..."
    docker-compose down
    docker-compose up -d
fi

# Wait for container to be ready
echo ""
echo "Waiting for container to be healthy..."
sleep 5

# Check container status
docker ps | grep -i rapid

# Get container logs
echo ""
echo "Recent container logs:"
CONTAINER_NAME=$(docker ps --format "table {{.Names}}" | grep -i rapid | head -1)
docker logs --tail=20 $CONTAINER_NAME

# Test CORS headers
echo ""
echo "=== Testing CORS Headers ==="
echo ""
echo "Testing from https://rapiddocs.io:"
curl -s -I -X OPTIONS https://api.rapiddocs.io/auth/login \
    -H "Origin: https://rapiddocs.io" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: content-type" \
    2>&1 | grep -E "(HTTP|Access-Control-Allow-Origin)" || echo "No CORS header found"

echo ""
echo "Testing authentication endpoint directly:"
response=$(curl -s -X POST https://api.rapiddocs.io/auth/login \
    -H "Content-Type: application/json" \
    -H "Origin: https://rapiddocs.io" \
    -d '{"email":"test@rapiddocs.io","password":"testuser"}' \
    2>/dev/null)

if echo "$response" | grep -q "access_token"; then
    echo "✅ Authentication successful!"
    echo "Response preview: $(echo "$response" | head -c 100)..."
elif echo "$response" | grep -q "Invalid email or password"; then
    echo "❌ Authentication failed: Invalid credentials"
    echo "Response: $response"
elif [ -z "$response" ]; then
    echo "❌ No response from server - check if backend is running"
else
    echo "❌ Unexpected response:"
    echo "$response" | head -c 500
fi

echo ""
echo "=== Checking Environment Variables in Container ==="
docker exec $CONTAINER_NAME sh -c 'echo $CORS_ORIGINS' || echo "Could not check env vars"

echo ""
echo "=== Instructions ==="
echo "If CORS is still not working:"
echo "1. Check if the container is reading the .env.production file"
echo "2. The container might be caching old environment variables"
echo "3. Try: docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME"
echo "4. Then rebuild: docker-compose up -d --build"
echo ""
echo "To verify the test user exists in MongoDB:"
echo "  - Database: docgen_prod"
echo "  - Collection: users"
echo "  - Email: test@rapiddocs.io"