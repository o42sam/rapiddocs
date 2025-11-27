# Google OAuth2 Setup Guide

This guide will walk you through setting up Google OAuth2 authentication for your application.

## Prerequisites

- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "RapidDocs Auth")
5. Click "Create"

## Step 2: Enable Google+ API

1. In your Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google+ API"
3. Click on it and click "Enable"
4. Also enable "Google OAuth2 API" if available

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" (unless you have a Google Workspace account)
3. Click "Create"
4. Fill in the required information:
   - **App name**: RapidDocs (or your app name)
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click "Save and Continue"
6. On the "Scopes" page, click "Add or Remove Scopes"
7. Add the following scopes:
   - `openid`
   - `email`
   - `profile`
8. Click "Save and Continue"
9. On the "Test users" page (for external apps in testing mode):
   - Add your email address as a test user
   - Click "Save and Continue"
10. Review and click "Back to Dashboard"

## Step 4: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application" as the application type
4. Enter a name (e.g., "RapidDocs Web Client")
5. Under "Authorized JavaScript origins", add:
   - `http://localhost:8000` (for local development)
   - `https://yourdomain.com` (for production)
6. Under "Authorized redirect URIs", add:
   - `http://localhost:8000/api/v1/auth/google/callback` (for local development)
   - `https://yourdomain.com/api/v1/auth/google/callback` (for production)
7. Click "Create"
8. **IMPORTANT**: Copy your "Client ID" and "Client Secret" - you'll need these!

## Step 5: Configure Environment Variables

1. Open your `.env` file in the backend directory
2. Add the following variables with your credentials:

```bash
# Google OAuth2
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

For production, update the redirect URI:
```bash
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/auth/google/callback
```

## Step 6: Test the Implementation

### Backend Testing

1. Start your FastAPI server:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

2. Open your browser and go to: `http://localhost:8000/api/v1/docs`

3. Test the following endpoints:

   **a) Initiate Google Login:**
   - Endpoint: `GET /api/v1/auth/google/login`
   - This returns an authorization URL
   - Open the URL in your browser
   - You'll be redirected to Google's login page

   **b) Handle Callback:**
   - After logging in with Google, you'll be redirected back to:
   - `http://localhost:8000/api/v1/auth/google/callback?code=...&state=...`
   - This endpoint processes the authentication and returns user data with JWT tokens

## API Endpoints

### 1. Initiate Google OAuth Login

**GET** `/api/v1/auth/google/login`

Returns:
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "random_state_token"
}
```

### 2. Google OAuth Callback

**GET** `/api/v1/auth/google/callback`

Query Parameters:
- `code`: Authorization code from Google
- `state`: State token for CSRF protection

Returns:
```json
{
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "username": "user_123456",
    "full_name": "John Doe",
    "credits": 40,
    "is_active": true,
    "is_verified": true,
    "oauth_provider": "google",
    "profile_picture": "https://lh3.googleusercontent.com/..."
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

## Frontend Integration

### Basic HTML/JavaScript Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Google OAuth Login</title>
</head>
<body>
    <button id="google-login-btn">Sign in with Google</button>

    <script>
        const API_BASE = 'http://localhost:8000/api/v1';

        document.getElementById('google-login-btn').addEventListener('click', async () => {
            try {
                // Step 1: Get authorization URL
                const response = await fetch(`${API_BASE}/auth/google/login`);
                const data = await response.json();

                // Step 2: Store state in sessionStorage for verification
                sessionStorage.setItem('oauth_state', data.state);

                // Step 3: Redirect to Google
                window.location.href = data.authorization_url;
            } catch (error) {
                console.error('Error initiating Google login:', error);
            }
        });

        // Handle callback after redirect
        window.addEventListener('load', () => {
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code');
            const state = urlParams.get('state');
            const storedState = sessionStorage.getItem('oauth_state');

            if (code && state && state === storedState) {
                // Authentication successful - tokens are in the callback response
                // Store tokens in localStorage
                const tokens = /* extract from callback response */;
                localStorage.setItem('access_token', tokens.access_token);
                localStorage.setItem('refresh_token', tokens.refresh_token);

                // Redirect to dashboard or home page
                window.location.href = '/dashboard';
            }
        });
    </script>
</body>
</html>
```

### React/TypeScript Example

```typescript
// GoogleLoginButton.tsx
import React from 'react';
import axios from 'axios';

const GoogleLoginButton: React.FC = () => {
  const handleGoogleLogin = async () => {
    try {
      const response = await axios.get(
        'http://localhost:8000/api/v1/auth/google/login'
      );

      const { authorization_url, state } = response.data;

      // Store state for verification
      sessionStorage.setItem('oauth_state', state);

      // Redirect to Google
      window.location.href = authorization_url;
    } catch (error) {
      console.error('Error initiating Google login:', error);
    }
  };

  return (
    <button onClick={handleGoogleLogin}>
      Sign in with Google
    </button>
  );
};

export default GoogleLoginButton;
```

```typescript
// GoogleCallbackHandler.tsx
import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const GoogleCallbackHandler: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const storedState = sessionStorage.getItem('oauth_state');

    if (code && state === storedState) {
      // The callback already processed authentication on the backend
      // Extract user data and tokens from the response
      // Store in your state management solution (Redux, Context, etc.)

      navigate('/dashboard');
    } else {
      navigate('/login?error=authentication_failed');
    }
  }, [searchParams, navigate]);

  return <div>Processing authentication...</div>;
};

export default GoogleCallbackHandler;
```

## Security Considerations

1. **HTTPS in Production**: Always use HTTPS in production
2. **State Token**: The state token prevents CSRF attacks - never skip it
3. **Secure Token Storage**: Store JWT tokens securely (httpOnly cookies are best)
4. **Token Expiration**: Access tokens expire after 1 hour, use refresh tokens
5. **Redirect URI Validation**: Google validates redirect URIs - ensure they match exactly

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Ensure the redirect URI in your Google Cloud Console matches exactly with `GOOGLE_REDIRECT_URI` in your `.env`
- Check for trailing slashes and http vs https

### Error: "invalid_client"
- Verify your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- Check that they're properly set in your `.env` file

### Error: "access_denied"
- User canceled the authorization
- User's email might not be in the test users list (if app is in testing mode)

### Error: "Invalid state token"
- State tokens expire after use
- Ensure you're not refreshing the callback page
- Check that state is properly stored and retrieved

## Production Deployment

Before deploying to production:

1. Update authorized origins and redirect URIs in Google Cloud Console
2. Update `GOOGLE_REDIRECT_URI` in production environment variables
3. Set appropriate CORS origins in your backend
4. Consider implementing rate limiting for OAuth endpoints
5. Use Redis or database for state token storage instead of in-memory dict
6. Enable logging for OAuth events
7. Implement proper error handling and user feedback

## Database Schema Updates

The User model now includes:

```python
class User(BaseModel):
    # ... existing fields ...
    oauth_provider: Optional[str] = None  # "google", "github", etc.
    oauth_id: Optional[str] = None  # Provider's user ID
    profile_picture: Optional[str] = None  # Profile picture URL
```

Users created via Google OAuth:
- Have `oauth_provider` set to "google"
- Have `oauth_id` set to their Google user ID
- Have `is_verified` set to True (Google emails are verified)
- Have `hashed_password` set to None (no password needed)
- Get auto-generated usernames based on email

## Support

For issues or questions:
- Check FastAPI logs: `uvicorn app.main:app --reload`
- Check Google Cloud Console audit logs
- Review the OAuth2 flow in your browser's network tab

## Additional Resources

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [FastAPI OAuth2 Guide](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)
- [Authlib Documentation](https://docs.authlib.org/)
