/**
 * Authentication Wrapper
 * Provides fallback to mock authentication when backend is unavailable
 */

import { authService, LoginCredentials, RegisterData, AuthResponse } from './authService';
import { mockAuthService } from './mockAuthService';

class AuthWrapper {
  private useMock: boolean = false;

  constructor() {
    // Check if we should use mock auth
    this.useMock = import.meta.env.VITE_USE_MOCK_AUTH === 'true';

    if (this.useMock) {
      console.warn('🔒 Using MOCK authentication - for testing only!');
    }
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    if (this.useMock) {
      return mockAuthService.register(data);
    }

    try {
      return await authService.register(data);
    } catch (error: any) {
      // If backend is unavailable and we're in development, offer mock mode
      if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
        console.error('Backend unavailable. Authentication requires a running backend server.');
        console.info('To use mock authentication for testing, set VITE_USE_MOCK_AUTH=true in .env');
        throw new Error('Authentication service unavailable. Please ensure the backend server is running.');
      }

      // Re-throw the original error if it's not a network issue
      throw error;
    }
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    if (this.useMock) {
      return mockAuthService.login(credentials);
    }

    try {
      return await authService.login(credentials);
    } catch (error: any) {
      // If backend is unavailable and we're in development, offer mock mode
      if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
        console.error('Backend unavailable. Authentication requires a running backend server.');
        console.info('To use mock authentication for testing, set VITE_USE_MOCK_AUTH=true in .env');

        // In development, provide demo credentials hint
        if (import.meta.env.DEV) {
          console.info('For testing: You can enable mock auth or deploy your backend.');
        }

        throw new Error('Authentication service unavailable. Please ensure the backend server is running.');
      }

      // Handle specific auth errors
      if (error.response?.status === 401) {
        throw new Error('Invalid email or password');
      }

      if (error.response?.status === 400) {
        throw new Error(error.response.data?.detail || 'Invalid request');
      }

      // Re-throw the original error
      throw error;
    }
  }

  async logout(): Promise<void> {
    if (this.useMock) {
      return mockAuthService.logout();
    }
    return authService.logout();
  }

  isAuthenticated(): boolean {
    if (this.useMock) {
      return mockAuthService.isAuthenticated();
    }
    return authService.isAuthenticated();
  }

  getUser(): any {
    if (this.useMock) {
      return mockAuthService.getCurrentUser();
    }
    return authService.getUser();
  }

  getAccessToken(): string | null {
    return authService.getAccessToken();
  }

  clearAuth(): void {
    return authService.clearAuth();
  }

  setupAxiosInterceptors(): void {
    return authService.setupAxiosInterceptors();
  }
}

export const authWrapper = new AuthWrapper();