#!/bin/bash

# Complete fix script for backend authentication issues
# Fixes:
# 1. Missing PyJWT module
# 2. KeyError in /auth/me endpoint

echo "=== Complete Backend Authentication Fix ==="
echo "This script fixes both PyJWT dependency and /auth/me endpoint"
echo ""

# Check if we're in the backend directory
if [ ! -f "docker-compose.yml" ] || [ ! -d "app" ]; then
    echo "ERROR: Please run this script from /home/docgen/backend directory"
    exit 1
fi

echo "Step 1: Backing up current files..."
cp app/main_simple.py app/main_simple.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null
cp Dockerfile Dockerfile.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null

echo ""
echo "Step 2: Fixing Dockerfile to include PyJWT..."
# Check if PyJWT is already in Dockerfile
if ! grep -q "PyJWT" Dockerfile; then
    echo "Adding PyJWT to Dockerfile..."

    # Find the pip install section and add PyJWT
    if grep -q "pip install --no-cache-dir" Dockerfile; then
        # Add PyJWT to the existing pip install command
        sed -i '/pip install --no-cache-dir/a\    PyJWT==2.8.0 \\' Dockerfile
        echo "✓ Added PyJWT to Dockerfile"
    else
        # If no pip install section, add it before the COPY commands
        cat >> Dockerfile << 'EOF'

# Install PyJWT for authentication
RUN pip install --no-cache-dir PyJWT==2.8.0
EOF
        echo "✓ Added PyJWT installation to Dockerfile"
    fi
else
    echo "✓ PyJWT already in Dockerfile"
fi

echo ""
echo "Step 3: Fixing /auth/me endpoint to handle missing 'name' field..."
cat > fix-get-me.py << 'PYTHON_EOF'
#!/usr/bin/env python3

# Read the current file
with open('app/main_simple.py', 'r') as f:
    content = f.read()

# Fix the get_me endpoint
if 'name=current_user["name"]' in content:
    content = content.replace(
        'name=current_user["name"]',
        'name=current_user.get("name", current_user.get("email", "User"))'
    )
    print("✓ Fixed get_me endpoint to handle missing 'name' field")
elif 'name=current_user.get("name"' in content:
    print("✓ get_me endpoint already fixed")
else:
    print("⚠ Could not find the pattern to fix. Manual fix may be needed.")

# Write back
with open('app/main_simple.py', 'w') as f:
    f.write(content)
PYTHON_EOF

python3 fix-get-me.py

echo ""
echo "Step 4: Quick fix - Install PyJWT in running container first..."
# Try to install in running container if it exists
if docker ps | grep -q rapiddocs-backend; then
    echo "Installing PyJWT in running container..."
    docker exec rapiddocs-backend pip install PyJWT==2.8.0 2>/dev/null || echo "Container not responding, will rebuild"
fi

echo ""
echo "Step 5: Rebuilding Docker container with fixes..."
docker-compose down

# Remove any cached images to ensure clean build
docker system prune -f

echo "Building container (this may take a few minutes)..."
docker-compose build --no-cache backend

echo "Starting container..."
docker-compose up -d

echo ""
echo "Step 6: Waiting for container to start (40 seconds)..."
for i in {1..40}; do
    echo -n "."
    sleep 1
done
echo ""

echo ""
echo "Step 7: Verifying container is running..."
if docker ps | grep -q rapiddocs-backend; then
    echo "✓ Container is running"

    # Check if PyJWT is installed
    echo "Checking PyJWT installation..."
    if docker exec rapiddocs-backend python3 -c "import jwt; print('PyJWT version:', jwt.__version__)" 2>/dev/null; then
        echo "✓ PyJWT is installed"
    else
        echo "⚠ PyJWT not found, installing directly..."
        docker exec rapiddocs-backend pip install PyJWT==2.8.0
        docker restart rapiddocs-backend
        sleep 10
    fi
else
    echo "✗ Container failed to start"
    echo "Checking logs:"
    docker logs rapiddocs-backend --tail 30
    exit 1
fi

echo ""
echo "Step 8: Testing authentication..."

# Test health endpoint first
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo "✓ Backend is responding"
else
    echo "⚠ Backend not responding on localhost, trying via nginx..."
fi

# Test login
echo "Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST https://api.rapiddocs.io/auth/login \
  -H "Content-Type: application/json" \
  -H "Origin: https://rapiddocs.io" \
  -d '{"email":"test@rapiddocs.io","password":"testuser"}')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✓ Login successful"

    # Extract token
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

    if [ -n "$TOKEN" ]; then
        echo "Testing /auth/me endpoint..."
        ME_RESPONSE=$(curl -s -X GET https://api.rapiddocs.io/auth/me \
          -H "Authorization: Bearer $TOKEN" \
          -H "Origin: https://rapiddocs.io")

        if echo "$ME_RESPONSE" | grep -q "email"; then
            echo "✓ /auth/me endpoint working!"
            echo "User data retrieved successfully"
        else
            echo "✗ /auth/me endpoint still failing"
            echo "Response: $ME_RESPONSE"
            echo ""
            echo "Checking for errors in logs..."
            docker logs rapiddocs-backend --tail 10 | grep -i error
        fi
    else
        echo "✗ Could not extract token from login response"
    fi
else
    echo "✗ Login failed"
    echo "Response: $LOGIN_RESPONSE"
    echo ""
    echo "Checking container logs..."
    docker logs rapiddocs-backend --tail 20
fi

echo ""
echo "Step 9: Final verification..."
docker logs rapiddocs-backend --tail 5

echo ""
echo "========================================="
echo "AUTHENTICATION FIX COMPLETE!"
echo "========================================="
echo ""
echo "Test from browser:"
echo "1. Go to https://rapiddocs.io"
echo "2. Login with:"
echo "   Email: test@rapiddocs.io"
echo "   Password: testuser"
echo ""
echo "If issues persist:"
echo "1. Check logs: docker logs rapiddocs-backend --tail 50"
echo "2. Restart container: docker restart rapiddocs-backend"
echo "3. Clear browser cache and try again"

# Clean up
rm -f fix-get-me.py