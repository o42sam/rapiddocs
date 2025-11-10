# Production Authentication Fix Guide

## Problem
When trying to generate documents in production at https://rapiddocs.io, users encounter a "not authenticated" error. This is caused by CORS (Cross-Origin Resource Sharing) configuration issues.

## Root Cause
The backend `.env` file only included localhost domains in `CORS_ORIGINS`:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

When the production frontend at `https://rapiddocs.io` tries to make API requests, the browser blocks them due to CORS policy violations.

## Solution

### 1. Update CORS Configuration in Production

**For Development (.env):**
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://rapiddocs.io
```

**For Production (.env.production):**
```bash
CORS_ORIGINS=https://rapiddocs.io,https://www.rapiddocs.io
```

### 2. Deployment Options

#### Option A: Use .env.production file
On your production server, rename or copy the production environment file:
```bash
cp backend/.env.production backend/.env
```

#### Option B: Set Environment Variables in Deployment Platform
If using a platform like Railway, Heroku, or AWS, set these environment variables in the platform's dashboard:
- `CORS_ORIGINS=https://rapiddocs.io,https://www.rapiddocs.io`
- `APP_ENV=production`
- `DEBUG=False`

### 3. Verify CORS Configuration

After deploying, verify CORS headers are being sent correctly:
```bash
curl -H "Origin: https://rapiddocs.io" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://your-api-url.com/api/v1/auth/login \
     -v
```

Look for these headers in the response:
```
Access-Control-Allow-Origin: https://rapiddocs.io
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: *
```

## Additional Production Checklist

### Security Settings

1. **Generate Strong JWT Secret Keys**
   ```bash
   # Generate new secret keys
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   Set these in production environment:
   ```
   JWT_SECRET_KEY=<generated-secret-1>
   JWT_REFRESH_SECRET_KEY=<generated-secret-2>
   ```

2. **Disable Debug Mode**
   ```
   DEBUG=False
   APP_ENV=production
   ```

3. **Secure MongoDB Connection**
   - Use TLS/SSL for MongoDB connection
   - Whitelist only production server IPs in MongoDB Atlas
   - Rotate MongoDB credentials regularly

### Frontend Configuration

Ensure the frontend is using the correct API URL in production:

**frontend/.env.production:**
```
VITE_API_BASE_URL=https://rapiddocs.io/api/v1
```

Or if backend is on a separate domain:
```
VITE_API_BASE_URL=https://api.rapiddocs.io/api/v1
```

### Testing Authentication Flow

1. **Test Login**
   ```bash
   curl -X POST https://rapiddocs.io/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -H "Origin: https://rapiddocs.io" \
        -d '{"email":"test@rapiddocs.io","password":"TestPass123!"}'
   ```

2. **Test Authenticated Request**
   ```bash
   curl -X GET https://rapiddocs.io/api/v1/auth/me \
        -H "Authorization: Bearer <access_token>" \
        -H "Origin: https://rapiddocs.io"
   ```

3. **Test Document Generation**
   ```bash
   curl -X POST https://rapiddocs.io/api/v1/generate/document \
        -H "Authorization: Bearer <access_token>" \
        -H "Origin: https://rapiddocs.io" \
        -F "description=Test document" \
        -F "length=500"
   ```

## Common Issues and Solutions

### Issue 1: "No 'Access-Control-Allow-Origin' header"
**Symptom:** Browser console shows CORS error
**Solution:** Verify CORS_ORIGINS includes your production domain

### Issue 2: "401 Unauthorized" after login
**Symptom:** Login succeeds but subsequent requests fail
**Solution:**
- Check that JWT tokens are being saved to localStorage
- Verify axios interceptors are set up correctly
- Check token expiration times

### Issue 3: "preflight request doesn't pass"
**Symptom:** OPTIONS requests failing
**Solution:** Ensure backend allows OPTIONS method and CORS headers

### Issue 4: Tokens working locally but not in production
**Symptom:** Authentication works in dev but fails in production
**Solution:**
- Verify production uses HTTPS (not HTTP)
- Check secure cookie settings if using cookies
- Ensure JWT_SECRET_KEY is set correctly in production

## Deployment Platforms

### Railway
1. Go to Variables section
2. Add each environment variable from `.env.production`
3. Redeploy the application

### Vercel/Netlify (Frontend)
1. Go to Environment Variables
2. Add `VITE_API_BASE_URL=https://rapiddocs.io/api/v1`
3. Rebuild the frontend

### AWS/GCP
1. Update environment variables in your deployment configuration
2. Restart the service

## Monitoring

After deployment, monitor:
1. **CORS Errors**: Check browser console and server logs
2. **Authentication Rate**: Track login success/failure rates
3. **Token Refresh**: Monitor token refresh endpoint usage
4. **API Response Times**: Ensure auth doesn't slow down requests

## Rollback Plan

If authentication issues persist:
1. Check server logs: `tail -f /var/log/your-app.log`
2. Verify environment variables: Check deployment platform settings
3. Test with curl: Use command-line tests to isolate frontend vs backend issues
4. Rollback if needed: Revert to previous working deployment

## Next Steps

1. ✅ Update CORS_ORIGINS to include production domain
2. ✅ Create .env.production with production settings
3. ⚠️ Generate strong JWT secret keys for production
4. ⚠️ Deploy updated configuration to production
5. ⚠️ Test authentication flow in production
6. ⚠️ Monitor for CORS/auth errors

## Support

If issues persist:
1. Check browser console for detailed error messages
2. Check backend logs for CORS rejection messages
3. Use browser DevTools Network tab to inspect request/response headers
4. Test API endpoints directly with curl to isolate the issue

---

**Last Updated:** 2025-11-10
**Status:** CORS configuration updated, ready for deployment
