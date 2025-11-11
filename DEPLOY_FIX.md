# Deploying Authentication Fix to Production

## Changes Made

Fixed critical authentication bug where API calls were using two different axios instances:
- ✅ `authService.ts` now uses shared `apiClient` instance
- ✅ All API requests now have authentication interceptors
- ✅ Token refresh works consistently across all endpoints

## Deployment Steps

### Option 1: Automatic Deployment (If Enabled)

Railway should automatically detect the GitHub push and redeploy:

1. **Check Railway Dashboard**:
   - Go to https://railway.app/dashboard
   - Open your `rapiddocs` project
   - Check the "Deployments" tab
   - You should see a new deployment triggered by commit `1cdd728`

2. **Wait for Build**:
   - Build takes 3-5 minutes
   - Watch the logs for "Build successful"
   - Wait for "Deployment successful"

3. **Verify Deployment**:
   - Visit https://rapiddocs.io
   - Try generating a document
   - Should now work without 403 errors

### Option 2: Manual Deployment (If Needed)

If automatic deployment isn't working:

**Using Railway Dashboard:**
1. Go to https://railway.app/dashboard
2. Select your project
3. Click on your service
4. Click "Deploy" → "Redeploy Latest"

**Using Railway CLI:**
```bash
# Install Railway CLI (if not installed)
npm i -g @railway/cli

# Login
railway login

# Link to project (if not linked)
railway link

# Trigger deployment
railway up

# Or force a redeploy
railway redeploy
```

### Option 3: Build Frontend Locally and Deploy

If you need to build the frontend separately:

```bash
# Build frontend
cd frontend
npm install
npm run build

# This creates frontend/dist with the compiled files
# The dist folder should be copied to backend/static during deployment
```

## Verification Steps

### 1. Check Deployment Status

**In Railway Dashboard:**
- Status should show "Active" (green)
- Last deployment should be commit `1cdd728`
- No errors in deployment logs

### 2. Test Authentication Flow

**Test in browser console (https://rapiddocs.io):**
```javascript
// Check if new version is deployed
console.log('Testing auth fix...');

// The fix is deployed if you see these files:
// - index-BDYefarM.js should have updated code
// - authService should use apiClient
```

### 3. Test Document Generation

1. **Login** to test account:
   - Email: test@rapiddocs.io
   - Password: TestPass123!
   - Credits: 999,999,829 (should be even less now from previous attempts)

2. **Generate a document**:
   - Go to /generate
   - Fill in form
   - Select "Formal" (34 credits)
   - Click "Generate Document"

3. **Expected behavior**:
   ```
   ✅ POST /api/v1/credits/deduct → 200 OK
   ✅ POST /api/v1/generate/document → 200 OK (not 403!)
   ✅ Document generation starts
   ✅ Progress bar shows
   ✅ Document downloads when complete
   ```

4. **Check browser console**:
   - Should NOT see "403 Forbidden"
   - Should NOT see "Not authenticated"
   - Should see "Credits deducted: 34"
   - Should see generation progress messages

### 4. Check Server Logs

**In Railway:**
1. Go to deployment logs
2. Look for:
   ```
   POST /api/v1/credits/deduct → 200 OK
   POST /api/v1/generate/document → 200 OK
   INFO: Starting document generation...
   ```

3. Should NOT see:
   ```
   403 Forbidden
   Could not validate credentials
   ```

## If Still Getting 403 Errors

### Issue: New Build Not Deployed

**Check:**
```bash
# View Railway logs
railway logs

# Look for:
# "Building..." → means new build is starting
# "Deployment successful" → means new version is live
```

**Solution:**
If no new build was triggered:
1. Go to Railway dashboard
2. Manually click "Deploy" → "Redeploy"
3. Wait for build to complete

### Issue: Cache Problem

**Browser cache might be serving old JavaScript files**

**Solution:**
1. Open https://rapiddocs.io
2. Open DevTools (F12)
3. Right-click refresh button → "Empty Cache and Hard Reload"
4. Or: Press Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

### Issue: Frontend Not Rebuilt

**The Dockerfile might not have rebuilt the frontend**

**Check Dockerfile:**
```dockerfile
# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim
# ... copies frontend/dist to backend/static
```

**Solution:**
If frontend wasn't rebuilt, trigger a full rebuild:
```bash
railway redeploy --force-rebuild
```

## Environment Variables to Check

Make sure these are set in Railway:

```bash
# Critical for production
CORS_ORIGINS=https://rapiddocs.io,https://www.rapiddocs.io

# Should be set
APP_ENV=production
DEBUG=False

# MongoDB
MONGODB_URL=mongodb+srv://...
MONGODB_DB_NAME=docgen

# API Keys
HUGGINGFACE_API_KEY=hf_...
```

## Rollback Plan (If Needed)

If the fix causes issues:

```bash
# Rollback to previous commit
git revert 1cdd728
git push gh-o42sam master

# Or rollback in Railway dashboard:
# Go to Deployments → Find previous working deployment → Click "Redeploy"
```

## Success Criteria

✅ No more 403 "Not authenticated" errors
✅ Credits deducted successfully
✅ Document generation starts without errors
✅ User can generate documents end-to-end
✅ Token refresh works automatically

## Timeline

- **Code committed**: ✅ Done
- **Pushed to GitHub**: ✅ Done
- **Railway auto-deploy**: ⏳ In progress (3-5 minutes)
- **Verification**: ⏳ Pending
- **Success**: 🎯 Goal

## Next Steps After Successful Deployment

1. ✅ Verify document generation works end-to-end
2. ✅ Test with different document types (formal vs infographic)
3. ✅ Monitor error logs for any issues
4. ✅ Test Bitcoin payment flow
5. ✅ Check background payment processor is running

---

**Commit deployed**: `1cdd728` - Fix authentication interceptor to use shared apiClient instance
**Date**: 2025-11-10
**Status**: Ready for deployment verification
