# Google OAuth2 Frontend Integration

## Overview

Google OAuth2 "Sign in with Google" buttons have been fully integrated into the RapidDocs frontend for both login and registration pages.

## Files Created/Modified

### New Files Created

1. **`src/ts/auth/googleOAuthService.ts`**
   - Service for handling Google OAuth2 flow
   - Functions:
     - `initiateLogin()` - Starts OAuth flow
     - `handleCallback()` - Processes OAuth callback
     - `isOAuthCallback()` - Checks if current URL is callback

2. **`src/ts/components/GoogleSignInButton.ts`**
   - Reusable Google sign-in button component
   - Features official Google branding
   - Loading states
   - Error handling

### Modified Files

1. **`src/ts/pages/LoginPage.ts`**
   - Added Google sign-in button
   - Button text: "Sign in with Google"
   - Integrated with existing error display

2. **`src/ts/pages/RegisterPage.ts`**
   - Added Google sign-up button
   - Button text: "Sign up with Google"
   - Integrated with existing error display

3. **`src/ts/main.ts`**
   - Added OAuth callback handler
   - Shows loading state during authentication
   - Error handling with user-friendly messages

## Features

### Google Sign-In Button
- Official Google branding with multi-color logo
- Smooth hover animations
- Loading spinner during authentication
- Consistent styling with existing UI

### User Experience
1. **Initiate Sign-In**:
   - User clicks "Sign in with Google"
   - Button shows loading state
   - Redirect to Google authorization

2. **Google Authorization**:
   - User authenticates with Google
   - Grants permissions
   - Redirected back to app

3. **Callback Handling**:
   - Loading spinner shown
   - Token exchange processed
   - User authenticated
   - Redirected to generate page

4. **Error Handling**:
   - Clear error messages
   - Option to retry
   - Fallback to email/password login

### Security Features
- CSRF protection with state tokens
- Session storage for state verification
- Token validation
- Secure redirect handling

## UI Components

### Login Page
```
┌─────────────────────────────────────┐
│         Welcome Back                │
│   Sign in to continue to RapidDocs │
├─────────────────────────────────────┤
│   Email: [________________]         │
│   Password: [________________]      │
│   [x] Remember me  Forgot password? │
│                                     │
│   [     Sign In     ]               │
│                                     │
│   ──── Or continue with ────        │
│                                     │
│   [🔵 Sign in with Google]          │
│                                     │
│   ──── Don't have an account? ────  │
│                                     │
│   [   Create Account   ]            │
└─────────────────────────────────────┘
```

### Register Page
```
┌─────────────────────────────────────┐
│        Create Account               │
│   Join RapidDocs and start creating │
├─────────────────────────────────────┤
│   Username: [________________]      │
│   Full Name: [________________]     │
│   Email: [________________]         │
│   Password: [________________]      │
│   Confirm: [________________]       │
│   [x] I agree to Terms              │
│                                     │
│   [   Create Account   ]            │
│                                     │
│   ──── Or continue with ────        │
│                                     │
│   [🔵 Sign up with Google]          │
│                                     │
│   ──── Already have an account? ──  │
│                                     │
│   [      Sign In      ]             │
└─────────────────────────────────────┘
```

## Authentication Flow

```
┌─────────────┐
│    User     │
│ clicks      │
│ "Sign in    │
│ with Google"│
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│ Frontend: googleOAuthService    │
│ - Generate CSRF state token     │
│ - Store in sessionStorage       │
│ - Request auth URL from backend │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Backend: /auth/google/login     │
│ - Generate authorization URL    │
│ - Return URL and state          │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Redirect to Google              │
│ User authenticates              │
│ Grants permissions              │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Callback to                     │
│ /api/v1/auth/google/callback    │
│ with code and state             │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Backend: Exchange code          │
│ - Verify state token            │
│ - Get access token from Google  │
│ - Fetch user info               │
│ - Create/login user             │
│ - Return JWT tokens             │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Frontend: Store tokens          │
│ - Save to localStorage          │
│ - Set auth state                │
│ - Navigate to /generate         │
└─────────────────────────────────┘
```

## Code Examples

### Using GoogleSignInButton Component

```typescript
import { GoogleSignInButton } from '../components/GoogleSignInButton';

// Create button with custom text and error handler
const googleButton = new GoogleSignInButton(
  'Sign in with Google',
  (error) => {
    // Handle error
    console.error('OAuth error:', error);
    showErrorMessage(error.message);
  }
);

// Insert button HTML
container.innerHTML = googleButton.getHTML();

// Attach event listener
const button = container.querySelector('.google-signin-btn') as HTMLButtonElement;
googleButton.attachEventListener(button);
```

### Manually Initiating OAuth

```typescript
import { googleOAuthService } from '../auth/googleOAuthService';

// Start OAuth flow
try {
  await googleOAuthService.initiateLogin();
  // User will be redirected to Google
} catch (error) {
  console.error('Failed to start OAuth:', error);
}
```

### Handling OAuth Callback

```typescript
import { googleOAuthService } from '../auth/googleOAuthService';

// Check if this is an OAuth callback
if (googleOAuthService.isOAuthCallback()) {
  try {
    await googleOAuthService.handleCallback();
    // User is now authenticated
  } catch (error) {
    console.error('OAuth callback failed:', error);
  }
}
```

## Styling

The Google button uses Tailwind CSS classes and matches the existing design:

```css
.google-signin-btn {
  @apply w-full flex items-center justify-center px-4 py-3;
  @apply border border-gray-300 rounded-lg shadow-sm;
  @apply bg-white text-gray-700 font-medium;
  @apply hover:bg-gray-50;
  @apply focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500;
  @apply transition;
}
```

## Testing

### Manual Testing

1. **Start servers**:
   ```bash
   # Backend
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload

   # Frontend
   cd frontend
   npm run dev
   ```

2. **Test Login Flow**:
   - Visit http://localhost:5173/login
   - Click "Sign in with Google"
   - Authenticate with Google
   - Verify redirect to /generate
   - Check user is logged in

3. **Test Register Flow**:
   - Visit http://localhost:5173/register
   - Click "Sign up with Google"
   - Authenticate with Google
   - Verify account creation
   - Check user is logged in

4. **Test Error Handling**:
   - Cancel Google authentication
   - Verify error message displays
   - Check user can retry

### Automated Testing

```typescript
// Example test with testing library
describe('Google OAuth Integration', () => {
  it('should display Google sign-in button', () => {
    const loginPage = new LoginPage();
    loginPage.render();

    const button = document.querySelector('.google-signin-btn');
    expect(button).toBeTruthy();
    expect(button.textContent).toContain('Sign in with Google');
  });

  it('should initiate OAuth flow on click', async () => {
    const loginPage = new LoginPage();
    loginPage.render();

    const button = document.querySelector('.google-signin-btn') as HTMLButtonElement;
    button.click();

    // Should redirect to Google
    expect(window.location.href).toContain('accounts.google.com');
  });
});
```

## Troubleshooting

### Button Not Appearing
- Check browser console for errors
- Verify imports are correct
- Ensure container element exists

### OAuth Flow Not Starting
- Check GOOGLE_CLIENT_ID is set in backend
- Verify backend is running
- Check network tab for API errors

### Callback Fails
- Verify GOOGLE_REDIRECT_URI matches exactly
- Check state token is stored
- Ensure backend credentials are correct

### User Not Logged In After Success
- Check localStorage for tokens
- Verify authState is updated
- Check navigation works

## Configuration

### Backend Environment Variables
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

### Frontend Environment Variables
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Browser Compatibility

- Chrome/Edge: ✅ Fully supported
- Firefox: ✅ Fully supported
- Safari: ✅ Fully supported
- Mobile browsers: ✅ Fully supported

## Accessibility

- Keyboard navigation supported
- Screen reader friendly
- Clear focus indicators
- ARIA labels included

## Future Enhancements

1. **Remember OAuth Choice**: Save preference for Google login
2. **Account Linking**: Link Google account to existing email account
3. **Profile Picture**: Display Google profile picture in UI
4. **Multiple Providers**: Add GitHub, Microsoft OAuth
5. **One-Tap Sign-In**: Google One Tap integration
6. **Progressive Enhancement**: Fallback for browsers without JS

## Security Best Practices

✅ CSRF protection with state tokens
✅ Secure token storage
✅ State validation
✅ HTTPS in production
✅ Token expiration handling
✅ Error sanitization

## Resources

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Backend OAuth Setup Guide](../backend/GOOGLE_OAUTH_SETUP.md)
- [Backend Implementation Summary](../backend/OAUTH_IMPLEMENTATION_SUMMARY.md)

## Support

For issues:
1. Check browser console for errors
2. Verify backend is running and configured
3. Test backend OAuth endpoints directly
4. Check network tab for failed requests

## Summary

✅ Google OAuth buttons integrated in Login and Register pages
✅ Full authentication flow implemented
✅ Error handling and loading states
✅ Mobile responsive design
✅ CSRF protection
✅ Seamless user experience
✅ Production-ready with configuration

Both frontend and backend are now fully integrated for Google OAuth2 authentication!
