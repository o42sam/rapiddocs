# Google OAuth2 Quick Start Guide

## 1. Get Google Credentials (5 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select existing
3. Click "Create Credentials" → "OAuth client ID"
4. Choose "Web application"
5. Add these URIs:
   - **Authorized redirect URIs**: `http://localhost:8000/api/v1/auth/google/callback`
6. Copy the **Client ID** and **Client Secret**

## 2. Configure Environment Variables

Add to `/home/taliban/doc-gen/backend/.env`:

```bash
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

## 3. Start the Server

```bash
cd /home/taliban/doc-gen/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

## 4. Test the Flow

### Option A: Using Browser
1. Visit: `http://localhost:8000/api/v1/auth/google/login`
2. Copy the `authorization_url` from the response
3. Paste it in your browser
4. Sign in with Google
5. You'll be redirected back with user data and tokens

### Option B: Using Swagger UI
1. Visit: `http://localhost:8000/api/v1/docs`
2. Try the `/auth/google/login` endpoint
3. Copy the authorization URL
4. Open in browser and complete authentication

## 5. API Endpoints

### Initiate Login
```bash
GET http://localhost:8000/api/v1/auth/google/login
```

### Callback (automatic)
```bash
GET http://localhost:8000/api/v1/auth/google/callback?code=...&state=...
```

## Frontend Integration Example

```html
<button onclick="loginWithGoogle()">Sign in with Google</button>

<script>
async function loginWithGoogle() {
  // Get authorization URL
  const res = await fetch('http://localhost:8000/api/v1/auth/google/login');
  const { authorization_url, state } = await res.json();

  // Save state for verification
  sessionStorage.setItem('oauth_state', state);

  // Redirect to Google
  window.location.href = authorization_url;
}
</script>
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | From Google Cloud Console | `123456.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console | `GOCSPX-abc123...` |
| `GOOGLE_REDIRECT_URI` | Your callback URL | `http://localhost:8000/api/v1/auth/google/callback` |

## Troubleshooting

**"redirect_uri_mismatch"**
→ Ensure redirect URI in Google Console matches exactly

**"invalid_client"**
→ Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are correct

**"Access denied"**
→ Add your email as a test user in Google Cloud Console

## Production Setup

For production, update:
1. Google Console: Add production redirect URI
2. `.env`: Update `GOOGLE_REDIRECT_URI` to production URL
3. Use HTTPS (required by Google)

Example production URI:
```bash
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/auth/google/callback
```

## Complete Documentation

See `GOOGLE_OAUTH_SETUP.md` for detailed instructions.
