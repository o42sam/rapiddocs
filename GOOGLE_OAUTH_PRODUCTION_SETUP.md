# Google OAuth Production Setup Guide

This guide will help you configure Google OAuth for the production environment of RapidDocs.

## Problem Summary

The Google OAuth callback wasn't working in production because the backend was missing critical environment variables:
- `GOOGLE_REDIRECT_URI` - The callback URL Google redirects to after authentication
- `FRONTEND_URL` - The base URL of your frontend application

These variables are needed for the backend to:
1. Construct the correct Google OAuth authorization URL
2. Redirect authenticated users back to the frontend's `/generate` page with tokens

## Prerequisites

1. A Google Cloud Project with OAuth 2.0 credentials configured
2. Access to your production backend environment variables
3. Your production domain (e.g., `https://rapiddocs.io`)

## Step 1: Configure Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **APIs & Services** → **Credentials**
4. Click on your OAuth 2.0 Client ID (or create one if it doesn't exist)
5. Add the following to **Authorized redirect URIs**:
   ```
   https://rapiddocs.io/api/v1/auth/google/callback
   ```
   (Replace `rapiddocs.io` with your actual domain)

6. Save the changes
7. Copy your **Client ID** and **Client Secret**

## Step 2: Update Backend Environment Variables

In your production backend environment (Railway, Render, AWS, etc.), set the following environment variables:

```bash
# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=your-actual-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret-here
GOOGLE_REDIRECT_URI=https://rapiddocs.io/api/v1/auth/google/callback
FRONTEND_URL=https://rapiddocs.io
```

**Important:**
- Replace the placeholder values with your actual credentials from Step 1
- Ensure `GOOGLE_REDIRECT_URI` matches exactly what you added to Google Cloud Console
- `FRONTEND_URL` should be your frontend's base URL (no trailing slash)

### For Different Hosting Platforms

#### Railway
```bash
railway variables set GOOGLE_CLIENT_ID="your-client-id"
railway variables set GOOGLE_CLIENT_SECRET="your-client-secret"
railway variables set GOOGLE_REDIRECT_URI="https://rapiddocs.io/api/v1/auth/google/callback"
railway variables set FRONTEND_URL="https://rapiddocs.io"
```

#### Render
1. Go to your service dashboard
2. Navigate to **Environment** tab
3. Add each variable with the **Add Environment Variable** button

#### AWS / Heroku / Other
Consult your platform's documentation for setting environment variables.

## Step 3: Update CORS Settings

Ensure your backend's `CORS_ORIGINS` includes your production frontend URL:

```bash
CORS_ORIGINS=https://rapiddocs.io,https://www.rapiddocs.io
```

This allows your frontend to make API requests to the backend.

## Step 4: Restart Your Backend

After setting the environment variables, restart your backend service to apply the changes.

```bash
# Railway
railway restart

# Or redeploy your service on your platform
```

## Step 5: Test the OAuth Flow

1. Visit your production site: `https://rapiddocs.io`
2. Click "Sign in with Google"
3. Verify you're redirected to Google's OAuth consent screen
4. After granting permissions, verify you're redirected back to:
   ```
   https://rapiddocs.io/generate?access_token=...&refresh_token=...&oauth_success=true
   ```
5. Verify the page shows "Sign In Successful!" and redirects to the document generation page
6. Verify you can access authenticated features

## OAuth Flow Diagram

```
User clicks "Sign in with Google"
    ↓
Frontend calls: GET /api/v1/auth/google/login
    ↓
Backend generates auth URL with state token
    ↓
User redirected to: https://accounts.google.com/o/oauth2/v2/auth?...
    ↓
User authorizes app on Google
    ↓
Google redirects to: https://rapiddocs.io/api/v1/auth/google/callback?code=...&state=...
    ↓
Backend exchanges code for tokens
    ↓
Backend creates/updates user in database
    ↓
Backend generates JWT tokens
    ↓
Backend redirects to: https://rapiddocs.io/generate?access_token=...&refresh_token=...
    ↓
Frontend extracts tokens from URL
    ↓
Frontend stores tokens in localStorage
    ↓
Frontend fetches user data: GET /api/v1/auth/me
    ↓
User is authenticated and ready to generate documents
```

## Troubleshooting

### Error: "redirect_uri_mismatch"
**Cause:** The redirect URI in your Google Cloud Console doesn't match the one in your backend.

**Solution:**
1. Check the exact error message from Google
2. Ensure `GOOGLE_REDIRECT_URI` in your backend matches **exactly** what's in Google Cloud Console
3. Common issues:
   - Missing `/api/v1` prefix
   - HTTP vs HTTPS
   - Trailing slash
   - Typo in domain name

### Error: "Invalid state token"
**Cause:** State token validation failed (CSRF protection).

**Solution:**
1. This usually happens if you're using multiple backend instances without shared state storage
2. For production, consider using Redis or a database to store state tokens instead of in-memory
3. Check that cookies are enabled in the browser

### Error: "Failed to fetch user info after OAuth"
**Cause:** Backend couldn't fetch user data with the access token.

**Solution:**
1. Check that your backend has internet access to reach Google's API
2. Verify the Google OAuth scopes include `email` and `profile`
3. Check backend logs for detailed error messages

### Users redirected to login page instead of generate page
**Cause:** `FRONTEND_URL` environment variable is not set correctly.

**Solution:**
1. Ensure `FRONTEND_URL=https://rapiddocs.io` is set in backend environment
2. Restart the backend after setting the variable
3. Check that the variable is loaded correctly by logging `settings.FRONTEND_URL` in your backend

### Tokens appear in URL but authentication fails
**Cause:** Frontend not extracting/storing tokens correctly.

**Solution:**
1. Open browser console and check for JavaScript errors
2. Verify tokens are being stored in localStorage:
   ```javascript
   console.log(localStorage.getItem('access_token'));
   ```
3. Check that the frontend is calling `/api/v1/auth/me` to fetch user data

## Security Notes

1. **Never commit credentials to git:** Always use environment variables
2. **Use HTTPS in production:** OAuth requires HTTPS for security
3. **Rotate secrets regularly:** Generate new Client Secret periodically
4. **Implement rate limiting:** Prevent abuse of OAuth endpoints
5. **Validate state tokens:** Already implemented for CSRF protection
6. **Clear URL parameters:** Frontend clears tokens from URL after storing them

## Environment Variable Checklist

Backend `.env.production`:
- [x] `GOOGLE_CLIENT_ID` - Your Google OAuth Client ID
- [x] `GOOGLE_CLIENT_SECRET` - Your Google OAuth Client Secret
- [x] `GOOGLE_REDIRECT_URI` - Backend callback URL (e.g., `https://rapiddocs.io/api/v1/auth/google/callback`)
- [x] `FRONTEND_URL` - Frontend base URL (e.g., `https://rapiddocs.io`)
- [x] `CORS_ORIGINS` - Includes frontend URL (e.g., `https://rapiddocs.io,https://www.rapiddocs.io`)
- [x] `JWT_SECRET_KEY` - Strong random key for JWT signing
- [x] `JWT_REFRESH_SECRET_KEY` - Different strong random key for refresh tokens

Frontend `.env.production`:
- [x] `VITE_API_BASE_URL` - Backend API URL (e.g., `https://rapiddocs.io/api/v1`)

## File Changes Made

The following files were updated to include the missing environment variables:

1. `backend/.env.production` - Added `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, and `FRONTEND_URL`
2. `backend/.env.production.example` - Added the same variables as template for others

## Support

If you encounter issues not covered in this guide:
1. Check backend logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test OAuth flow in development first
4. Review Google Cloud Console Credentials configuration

## Summary

The OAuth callback flow is now properly configured to:
1. Accept the Google OAuth callback at the backend (`/api/v1/auth/google/callback`)
2. Redirect authenticated users to the frontend document generation page (`/generate`)
3. Pass JWT tokens via URL parameters
4. Frontend extracts tokens, stores them, and fetches user data
5. User is ready to generate documents

**Next Steps:**
1. Set the environment variables in your production backend
2. Restart the backend service
3. Test the complete OAuth flow
4. Monitor logs for any issues
