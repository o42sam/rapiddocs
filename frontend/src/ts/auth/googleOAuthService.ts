import axios from 'axios';
import { authState } from './authState';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface GoogleAuthResponse {
  authorization_url: string;
  state: string;
}

class GoogleOAuthService {
  /**
   * Initiate Google OAuth login flow
   * Stores state token and redirects to Google authorization URL
   */
  async initiateLogin(): Promise<void> {
    try {
      const response = await axios.get<GoogleAuthResponse>(
        `${API_BASE_URL}/auth/google/login`
      );

      const { authorization_url, state } = response.data;

      // Store state token in session storage for verification
      sessionStorage.setItem('google_oauth_state', state);

      // Store redirect URL if we're coming from somewhere specific
      const currentPath = window.location.pathname;
      if (currentPath !== '/login' && currentPath !== '/register') {
        sessionStorage.setItem('oauth_redirect_after', currentPath);
      }

      // Redirect to Google authorization URL
      window.location.href = authorization_url;
    } catch (error: any) {
      console.error('Failed to initiate Google OAuth:', error);
      throw new Error(
        error.response?.data?.detail || 'Failed to initiate Google sign in'
      );
    }
  }

  /**
   * Handle OAuth callback from Google
   * Backend redirects here with tokens in URL after successful authentication
   */
  async handleCallback(): Promise<void> {
    const urlParams = new URLSearchParams(window.location.search);
    const accessToken = urlParams.get('access_token');
    const refreshToken = urlParams.get('refresh_token');
    const oauthSuccess = urlParams.get('oauth_success');
    const error = urlParams.get('error');

    // Check for errors from backend
    if (error) {
      let errorMessage = 'Google authorization failed';
      switch (error) {
        case 'missing_code':
          errorMessage = 'Authorization code is missing';
          break;
        case 'invalid_state':
          errorMessage = 'Invalid state token - possible security issue';
          break;
        case 'token_exchange_failed':
          errorMessage = 'Failed to exchange authorization code';
          break;
        case 'no_access_token':
          errorMessage = 'Access token not received';
          break;
        case 'failed_to_get_user_info':
          errorMessage = 'Failed to get user information from Google';
          break;
        case 'missing_user_info':
          errorMessage = 'Required user information missing';
          break;
        case 'server_error':
          errorMessage = 'Server error during authentication';
          break;
        default:
          errorMessage = `Google authorization failed: ${error}`;
      }
      throw new Error(errorMessage);
    }

    // Validate that we have tokens from successful OAuth
    if (!oauthSuccess || !accessToken || !refreshToken) {
      throw new Error('Authentication failed - tokens not received');
    }

    try {
      // Store tokens
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);

      // Fetch user information with the new token
      const response = await axios.get(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${accessToken}`
        }
      });

      // Set authenticated state
      authState.setAuthenticated(response.data);

      // Clean up URL by removing token parameters (for security)
      const cleanUrl = window.location.pathname;
      window.history.replaceState({}, document.title, cleanUrl);

      // Small delay to ensure state propagates
      await new Promise(resolve => setTimeout(resolve, 100));

      console.log('OAuth authentication successful');
    } catch (error: any) {
      console.error('Failed to fetch user info after OAuth:', error);
      // Clear potentially invalid tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      throw new Error('Failed to complete authentication');
    }
  }

  /**
   * Check if current URL is an OAuth callback
   */
  isOAuthCallback(): boolean {
    const urlParams = new URLSearchParams(window.location.search);
    // Check for either OAuth success with tokens or OAuth error
    return (
      urlParams.has('oauth_success') ||
      (urlParams.has('error') && urlParams.get('error') !== null)
    );
  }
}

export const googleOAuthService = new GoogleOAuthService();
