import axios from 'axios';
import { authState } from './authState';
import { router } from '../router';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface GoogleAuthResponse {
  authorization_url: string;
  state: string;
}

interface AuthResponse {
  user: {
    id: string;
    email: string;
    username: string;
    full_name: string | null;
    credits: number;
    is_active: boolean;
    is_verified: boolean;
    oauth_provider: string | null;
    profile_picture: string | null;
    created_at: string;
  };
  tokens: {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  };
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
   * Exchanges code for tokens and authenticates user
   */
  async handleCallback(): Promise<void> {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const error = urlParams.get('error');

    // Check for errors
    if (error) {
      throw new Error(`Google authorization failed: ${error}`);
    }

    // Validate required parameters
    if (!code || !state) {
      throw new Error('Missing authorization code or state');
    }

    // Verify state token
    const storedState = sessionStorage.getItem('google_oauth_state');
    if (state !== storedState) {
      throw new Error('Invalid state token - possible CSRF attack');
    }

    // Clean up stored state
    sessionStorage.removeItem('google_oauth_state');

    try {
      // Exchange code for tokens via backend
      const response = await axios.get<AuthResponse>(
        `${API_BASE_URL}/auth/google/callback`,
        {
          params: { code, state }
        }
      );

      const { user, tokens } = response.data;

      // Store tokens
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);

      // Set authenticated state
      authState.setAuthenticated(user);

      // Get redirect URL or default to /generate
      const redirectTo = sessionStorage.getItem('oauth_redirect_after') || '/generate';
      sessionStorage.removeItem('oauth_redirect_after');

      // Small delay to ensure state propagates
      await new Promise(resolve => setTimeout(resolve, 50));

      // Navigate to destination
      router.navigate(redirectTo);
    } catch (error: any) {
      console.error('OAuth callback failed:', error);
      throw new Error(
        error.response?.data?.detail || 'Failed to complete Google sign in'
      );
    }
  }

  /**
   * Check if current URL is an OAuth callback
   */
  isOAuthCallback(): boolean {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.has('code') && urlParams.has('state');
  }
}

export const googleOAuthService = new GoogleOAuthService();
