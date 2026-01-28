#!/bin/bash

# Fix script for /auth/me endpoint - handles missing 'name' field
# This fixes the KeyError: 'name' issue when calling GET /auth/me

echo "=== Fixing /auth/me Endpoint ==="
echo "This script fixes the KeyError when the user doesn't have a 'name' field"
echo ""

# Check if we're in the backend directory
if [ ! -f "docker-compose.yml" ] || [ ! -d "app" ]; then
    echo "ERROR: Please run this script from /home/docgen/backend directory"
    exit 1
fi

echo "Step 1: Backing up current main_simple.py..."
cp app/main_simple.py app/main_simple.py.backup.$(date +%Y%m%d_%H%M%S)

echo ""
echo "Step 2: Creating Python script to fix the endpoint..."
cat > fix-get-me.py << 'PYTHON_EOF'
#!/usr/bin/env python3

# Read the current file
with open('app/main_simple.py', 'r') as f:
    content = f.read()

# Find the get_me function and fix it
# Look for the line with name=current_user["name"], and replace with .get()
import re

# Pattern to find the get_me function
pattern = r'(@app\.get\("/auth/me".*?async def get_me.*?return UserResponse\(.*?)name=current_user\["name"\](.*?\))'

# Check if pattern exists
if re.search(pattern, content, re.DOTALL):
    # Replace direct dictionary access with .get() method
    content = re.sub(
        pattern,
        r'\1name=current_user.get("name", current_user.get("email", "User"))\2',
        content,
        flags=re.DOTALL
    )
    print("✓ Fixed get_me endpoint to handle missing 'name' field")
else:
    # Alternative pattern - simpler replacement
    if 'name=current_user["name"]' in content:
        content = content.replace(
            'name=current_user["name"]',
            'name=current_user.get("name", current_user.get("email", "User"))'
        )
        print("✓ Fixed get_me endpoint using simple replacement")
    else:
        print("⚠ Could not find the pattern to fix. Manual fix may be needed.")

# Write back
with open('app/main_simple.py', 'w') as f:
    f.write(content)
PYTHON_EOF

echo ""
echo "Step 3: Running the Python fix script..."
python3 fix-get-me.py

echo ""
echo "Step 4: Verifying the fix..."
if grep -q 'name=current_user.get("name"' app/main_simple.py; then
    echo "✓ Fix applied successfully"
else
    echo "⚠ Fix may not have been applied correctly, checking alternative..."
    if grep -q 'name=current_user\["name"\]' app/main_simple.py; then
        echo "ERROR: The old pattern still exists. Manual fix needed."
        echo "Please manually edit app/main_simple.py and change:"
        echo '  name=current_user["name"]'
        echo "to:"
        echo '  name=current_user.get("name", current_user.get("email", "User"))'
    fi
fi

echo ""
echo "Step 5: Rebuilding Docker container..."
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d

echo ""
echo "Step 6: Waiting for container to start (30 seconds)..."
for i in {1..30}; do
    echo -n "."
    sleep 1
done
echo ""

echo ""
echo "Step 7: Testing the fixed endpoint..."

# Test login first
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
            echo "Response: $ME_RESPONSE"
        else
            echo "✗ /auth/me endpoint still failing"
            echo "Response: $ME_RESPONSE"
            echo ""
            echo "Checking Docker logs for errors:"
            docker logs rapiddocs-backend --tail 20
        fi
    else
        echo "✗ Could not extract token from login response"
    fi
else
    echo "✗ Login failed"
    echo "Response: $LOGIN_RESPONSE"
fi

echo ""
echo "========================================="
echo "FIX DEPLOYMENT COMPLETE!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Test authentication from browser at https://rapiddocs.io"
echo "2. Login with:"
echo "   Email: test@rapiddocs.io"
echo "   Password: testuser"
echo ""
echo "If issues persist, check:"
echo "1. Docker logs: docker logs rapiddocs-backend --tail 50"
echo "2. Try clearing browser cache"

# Clean up
rm -f fix-get-me.py