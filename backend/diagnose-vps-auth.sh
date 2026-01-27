#!/bin/bash

# Diagnostic script to find auth issues on VPS
echo "=== RapidDocs Authentication Diagnostic ==="
echo "Run this on the VPS to diagnose auth issues"
echo ""

# 1. Find the backend directory
echo "1. Checking backend locations:"
for dir in /root/rapiddocs-backend /home/docgen/backend /opt/rapiddocs/backend; do
    if [ -d "$dir" ]; then
        echo "  ✅ Found: $dir"
        if [ -f "$dir/.env.production" ]; then
            echo "     - Has .env.production"
            echo "     - CORS setting: $(grep '^CORS_ORIGINS=' $dir/.env.production | head -c 80)..."
        fi
        if [ -f "$dir/docker-compose.yml" ]; then
            echo "     - Has docker-compose.yml"
        fi
    fi
done

echo ""
echo "2. Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(NAME|rapid)" || echo "No RapidDocs container found"

echo ""
echo "3. Container environment:"
CONTAINER=$(docker ps --format "{{.Names}}" | grep -i rapid | head -1)
if [ ! -z "$CONTAINER" ]; then
    echo "   Container: $CONTAINER"
    echo "   CORS_ORIGINS env var:"
    docker exec $CONTAINER printenv CORS_ORIGINS 2>/dev/null || echo "   Not set in container environment"

    echo ""
    echo "   Checking if .env file is mounted:"
    docker inspect $CONTAINER | grep -A5 "Mounts" | grep -E "(Source|Destination)" || echo "No mounts found"
fi

echo ""
echo "4. Testing endpoints:"

echo ""
echo "   a) Health check (should work):"
curl -s https://api.rapiddocs.io/health | head -c 100

echo ""
echo ""
echo "   b) Auth endpoint (OPTIONS - CORS preflight):"
curl -s -I -X OPTIONS https://api.rapiddocs.io/auth/login \
    -H "Origin: https://rapiddocs.io" \
    -H "Access-Control-Request-Method: POST" \
    2>&1 | grep -E "(HTTP|Access-Control)"

echo ""
echo ""
echo "   c) Auth endpoint (POST - actual login):"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST https://api.rapiddocs.io/auth/login \
    -H "Content-Type: application/json" \
    -H "Origin: https://rapiddocs.io" \
    -d '{"email":"test@rapiddocs.io","password":"testuser"}' \
    2>/dev/null)

http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
body=$(echo "$response" | grep -v "HTTP_CODE:")

echo "   HTTP Status: $http_code"
if [ "$http_code" = "200" ]; then
    echo "   ✅ Authentication successful"
elif [ "$http_code" = "401" ]; then
    echo "   ❌ Authentication failed (401)"
    echo "   Response: $body"
elif [ "$http_code" = "404" ]; then
    echo "   ❌ Endpoint not found (404) - check if /auth/login exists"
elif [ "$http_code" = "000" ]; then
    echo "   ❌ Connection failed - backend might be down"
else
    echo "   ❌ Unexpected status code: $http_code"
    echo "   Response: $body"
fi

echo ""
echo "5. Checking nginx configuration:"
if [ -f /etc/nginx/sites-enabled/api.rapiddocs.io ]; then
    echo "   Nginx config found:"
    grep -E "(proxy_pass|location)" /etc/nginx/sites-enabled/api.rapiddocs.io | head -10
else
    echo "   No nginx config found for api.rapiddocs.io"
fi

echo ""
echo "6. Testing direct container access (bypassing nginx):"
CONTAINER_PORT=$(docker ps --format "table {{.Ports}}" | grep -i "8000" | sed 's/.*0.0.0.0:\([0-9]*\)->8000.*/\1/' | head -1)
if [ ! -z "$CONTAINER_PORT" ]; then
    echo "   Container port: $CONTAINER_PORT"
    echo "   Direct test:"
    curl -s -X POST http://localhost:$CONTAINER_PORT/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"test@rapiddocs.io","password":"testuser"}' \
        2>/dev/null | head -c 200
else
    echo "   Could not find container port mapping"
fi

echo ""
echo ""
echo "=== MongoDB Test User Check ==="
echo "To verify the test user exists, you need to:"
echo "1. Connect to MongoDB Atlas (docgen_prod database)"
echo "2. Check the 'users' collection for email: test@rapiddocs.io"
echo "3. Ensure the user has:"
echo "   - password field (bcrypt hashed)"
echo "   - credits: 999999"
echo "   - is_active: true"
echo ""
echo "Or run this Python script on the VPS:"
cat << 'PYTHON_SCRIPT'

python3 << 'EOF'
import asyncio
import motor.motor_asyncio
from datetime import datetime

MONGODB_URL = "mongodb+srv://samscarfaceegbo:G7a1n14G7@cluster1.vehwbxh.mongodb.net/?appName=Cluster1"
MONGODB_DB_NAME = "docgen_prod"

async def check_user():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]

    user = await db.users.find_one({"email": "test@rapiddocs.io"})
    if user:
        print(f"✅ User found in {MONGODB_DB_NAME}.users")
        print(f"   ID: {user.get('_id')}")
        print(f"   Username: {user.get('username')}")
        print(f"   Has password: {'Yes' if user.get('password') or user.get('hashedPassword') else 'No'}")
        print(f"   Credits: {user.get('credits', 0)}")
        print(f"   Active: {user.get('is_active', False)}")
    else:
        print(f"❌ User NOT found in {MONGODB_DB_NAME}.users")

        # Check if in wrong database
        db_old = client["docgen"]
        user_old = await db_old.users.find_one({"email": "test@rapiddocs.io"})
        if user_old:
            print(f"   ⚠️ But found in docgen.users (wrong database!)")

    client.close()

asyncio.run(check_user())
EOF
PYTHON_SCRIPT

echo ""
echo "=== Summary ==="
echo "Common issues:"
echo "1. CORS not updated in container (needs restart with new env)"
echo "2. Test user in wrong MongoDB database (docgen vs docgen_prod)"
echo "3. Nginx not forwarding /auth/* routes properly"
echo "4. Container not exposing port 8000 correctly"