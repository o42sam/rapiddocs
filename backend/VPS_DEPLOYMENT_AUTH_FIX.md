# VPS Deployment Instructions - Authentication Fix
## Date: January 28, 2026

### Issue Summary
The browser authentication was failing with `net::ERR_FAILED` because the backend CORS configuration had hardcoded values and wildcards that were causing header conflicts. The fix removes hardcoded CORS origins and uses environment variables properly.

### Changes Made
1. **Fixed CORS Configuration** in `backend/app/main_simple.py`:
   - Removed hardcoded `allow_origins=["*"]`
   - Removed duplicate CORS middleware configuration
   - Now properly reads `CORS_ORIGINS` from environment variables
   - Eliminates the "multiple values" header conflict error

2. **Environment Variables** in `backend/.env.production`:
   - Properly configured CORS_ORIGINS with all production domains
   - Includes custom domain (https://rapiddocs.io) and Firebase domains

---

## DEPLOYMENT INSTRUCTIONS

### Method 1: Using Git Pull (Recommended)

```bash
# 1. SSH into the VPS
ssh root@api.rapiddocs.io

# 2. Navigate to the backend directory
cd /home/docgen/backend

# 3. Stash any local changes
git stash

# 4. Pull the latest changes from master
git pull origin master

# 5. Verify the changes were pulled
git log -1 --oneline
# Should show: "fix: Remove hardcoded CORS and use environment variables"

# 6. Check that main_simple.py has the correct CORS configuration
grep -A 5 "CORSMiddleware" app/main_simple.py
# Should NOT show allow_origins=["*"]

# 7. Rebuild and restart the Docker container (IMPORTANT: use --no-cache)
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d

# 8. Wait for container to fully start (about 30 seconds)
sleep 30

# 9. Verify the container is running
docker ps | grep backend

# 10. Test the CORS headers
curl -I -X OPTIONS https://api.rapiddocs.io/auth/login \
  -H "Origin: https://rapiddocs.io" \
  -H "Access-Control-Request-Method: POST"
# Should return: Access-Control-Allow-Origin: https://rapiddocs.io
```

### Method 2: Manual File Update (If Git Pull Fails)

```bash
# 1. SSH into the VPS
ssh root@api.rapiddocs.io

# 2. Navigate to the backend directory
cd /home/docgen/backend

# 3. Backup the current main_simple.py
cp app/main_simple.py app/main_simple.py.backup

# 4. Download the fixed version directly
wget -O app/main_simple.py \
  https://raw.githubusercontent.com/o42sam/rapiddocs/master/backend/app/main_simple.py

# 5. Verify .env.production has correct CORS_ORIGINS
cat .env.production | grep CORS_ORIGINS
# Should show: CORS_ORIGINS=["https://rapiddocs.io","https://www.rapiddocs.io","https://rapiddocs-9a3f8.web.app"]

# 6. If CORS_ORIGINS is not correct, update it:
echo 'CORS_ORIGINS=["https://rapiddocs.io","https://www.rapiddocs.io","https://rapiddocs-9a3f8.web.app"]' >> .env.production

# 7. Rebuild and restart the Docker container
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d

# 8. Wait for container to start
sleep 30

# 9. Verify the fix
docker logs backend --tail 50
# Should not show any CORS errors
```

---

## VERIFICATION STEPS

### 1. Check Docker Container Status
```bash
docker ps
# Should show the backend container running

docker logs backend --tail 100
# Check for any startup errors
```

### 2. Test CORS Headers
```bash
# Test from rapiddocs.io origin
curl -I -X OPTIONS https://api.rapiddocs.io/auth/login \
  -H "Origin: https://rapiddocs.io" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"

# Should return:
# Access-Control-Allow-Origin: https://rapiddocs.io
# Access-Control-Allow-Methods: *
# Access-Control-Allow-Headers: *
```

### 3. Test Authentication Endpoint
```bash
# Test login with the test user
curl -X POST https://api.rapiddocs.io/auth/login \
  -H "Content-Type: application/json" \
  -H "Origin: https://rapiddocs.io" \
  -d '{"email":"test@rapiddocs.io","password":"testuser"}'

# Should return JSON with access_token and refresh_token
```

### 4. Test from Browser
1. Open Chrome DevTools (F12)
2. Go to https://rapiddocs.io
3. Try to login with:
   - Email: `test@rapiddocs.io`
   - Password: `testuser`
4. Check Network tab - should see successful `/auth/login` request
5. Should NOT see `net::ERR_FAILED` or CORS errors

---

## TROUBLESHOOTING

### If CORS errors persist after deployment:

1. **Check if Docker is using cached layers:**
```bash
# Force rebuild without cache
docker-compose down
docker system prune -f
docker-compose build --no-cache backend
docker-compose up -d
```

2. **Verify environment variables inside container:**
```bash
docker exec backend env | grep CORS
# Should show CORS_ORIGINS with correct domains
```

3. **Check the actual code inside the container:**
```bash
docker exec backend cat /app/app/main_simple.py | grep -A 10 "CORSMiddleware"
# Should NOT show allow_origins=["*"]
```

4. **Restart nginx if needed:**
```bash
systemctl restart nginx
```

5. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   - Or open in Incognito/Private mode

### If login still fails:

1. **Verify MongoDB has test user:**
```bash
docker exec backend python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv('.env.production')
client = MongoClient(os.getenv('MONGODB_URL'))
db = client['docgen_prod']
user = db.users.find_one({'email': 'test@rapiddocs.io'})
print('User found:', user['email'] if user else 'NOT FOUND')
print('Credits:', user.get('credits', 0) if user else 'N/A')
"
```

2. **Check API is accessible:**
```bash
curl https://api.rapiddocs.io/health
# Should return {"status":"ok"}
```

---

## ROLLBACK PROCEDURE (If Needed)

```bash
# 1. Restore backup
cd /home/docgen/backend
cp app/main_simple.py.backup app/main_simple.py

# 2. Rebuild container
docker-compose down
docker-compose up -d --build

# 3. Check previous commit
git log --oneline -5
git checkout <previous-commit-hash>
```

---

## IMPORTANT NOTES

1. **Always use `--no-cache` when rebuilding** to ensure Docker doesn't use cached layers
2. **Wait at least 30 seconds** after `docker-compose up -d` for the container to fully start
3. **Test from actual browser** after deployment, not just curl
4. **Keep the test user credentials** for future testing:
   - Email: `test@rapiddocs.io`
   - Password: `testuser`
   - Credits: 999,999 (for testing all document types)

---

## Contact for Issues
If you encounter any issues during deployment:
1. Check Docker logs: `docker logs backend --tail 200`
2. Check nginx logs: `tail -f /var/log/nginx/error.log`
3. Verify all services are running: `docker ps` and `systemctl status nginx`

Last Updated: January 28, 2026
Fix Commit: "fix: Remove hardcoded CORS and use environment variables"