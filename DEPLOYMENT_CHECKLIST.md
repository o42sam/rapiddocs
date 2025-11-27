# Deployment Checklist for RapidDocs

## Issue Fixed
✅ SPA routing issue - `/generate` endpoint returning 404 in production

## Changes Made

### 1. Backend (app/main.py)
- ✅ Added catch-all route for SPA routing
- ✅ Route serves `index.html` for all non-API paths
- ✅ Preserves API routes (prefixed with `/api/`)

### 2. Frontend (Loading Screen)
- ✅ Created `LoadingScreen.ts` component
- ✅ Added pulsating animation for logo
- ✅ Added thin progress bar at top
- ✅ Integrated with router for automatic page transitions

## Deployment Steps

### Step 1: Build Frontend
```bash
cd frontend
npm run build
```

### Step 2: Copy Static Files
```bash
# Copy built frontend to backend static directory
cp -r dist/* ../backend/static/
```

### Step 3: Test Locally (Optional)
```bash
cd backend
uvicorn app.main:app --reload

# Test these URLs in browser:
# http://localhost:8000/
# http://localhost:8000/generate
# http://localhost:8000/login
# http://localhost:8000/api/v1/docs
```

### Step 4: Deploy to Production

#### If using Railway/Heroku/similar:
```bash
git add .
git commit -m "Fix SPA routing and add loading screen"
git push origin master
```

#### If using Docker:
```bash
docker build -t rapiddocs .
docker push <registry>/rapiddocs:latest
```

#### If using direct deployment:
```bash
# SSH into server
ssh user@rapiddocs.io

# Pull latest code
cd /path/to/doc-gen
git pull

# Rebuild frontend
cd frontend
npm install
npm run build
cp -r dist/* ../backend/static/

# Restart backend
cd ../backend
# If using systemd:
sudo systemctl restart rapiddocs

# If using PM2:
pm2 restart rapiddocs

# If using Docker:
docker-compose down && docker-compose up -d
```

### Step 5: Verify Production

Test these URLs in production:

- [ ] `https://rapiddocs.io/` - Homepage loads
- [ ] `https://rapiddocs.io/generate` - Generate page loads (NOT 404)
- [ ] `https://rapiddocs.io/login` - Login page loads
- [ ] `https://rapiddocs.io/register` - Register page loads
- [ ] `https://rapiddocs.io/pricing` - Pricing page loads
- [ ] `https://rapiddocs.io/api/v1/docs` - API docs accessible

### Step 6: Test Loading Screen

- [ ] Navigate between pages - loading screen should appear briefly
- [ ] Logo should pulsate smoothly
- [ ] Progress bar should move from left to right
- [ ] Loading screen should fade out after page loads

### Step 7: Test API Endpoints

Using the generate page or API testing tool:

- [ ] POST `https://rapiddocs.io/api/v1/generate/document` - Works correctly
- [ ] GET `https://rapiddocs.io/api/v1/generate/status/{job_id}` - Works correctly
- [ ] GET `https://rapiddocs.io/api/v1/generate/download/{job_id}` - Works correctly

## Rollback Plan

If something goes wrong:

```bash
# Revert the catch-all route
git revert <commit-hash>
git push origin master

# Or manually remove lines 116-129 from app/main.py
```

## Environment Variables

Ensure these are set in production:

```bash
MONGODB_URL=<your-mongodb-url>
HUGGINGFACE_API_KEY=<your-api-key>
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
FRONTEND_URL=https://rapiddocs.io
GOOGLE_REDIRECT_URI=https://rapiddocs.io/api/v1/auth/google/callback
CORS_ORIGINS=https://rapiddocs.io
BITCOIN_PERSONAL_WALLET=<your-bitcoin-wallet>
PAYSTACK_SECRET_KEY=<your-paystack-key>
JWT_SECRET_KEY=<secure-random-string>
JWT_REFRESH_SECRET_KEY=<another-secure-random-string>
```

## Post-Deployment Monitoring

Monitor these logs for errors:

```bash
# Application logs
tail -f /var/log/rapiddocs/app.log

# Or if using Docker:
docker logs -f rapiddocs-backend

# Or if using PM2:
pm2 logs rapiddocs
```

Look for:
- ✅ No 404 errors for frontend routes
- ✅ API endpoints responding correctly
- ✅ No CORS errors in browser console
- ✅ Database connections successful

## Success Criteria

- ✅ Users can access all frontend pages without 404 errors
- ✅ Loading screen appears during page transitions
- ✅ API endpoints work correctly
- ✅ Document generation completes successfully
- ✅ No console errors in browser developer tools

## Support

If issues persist:
1. Check backend logs for errors
2. Check browser console for frontend errors
3. Verify environment variables are set correctly
4. Test API endpoints with curl or Postman
5. Review `SPA_ROUTING_FIX.md` for technical details

---

**Last Updated**: 2025-11-27
**Version**: 1.1.0
