/**
 * Mock Authentication Service
 * Used for testing when backend is not available
 */

import { AuthResponse, User, AuthTokens } from './authService';

class MockAuthService {
  private mockUser: User = {
    id: 'mock-user-123',
    email: 'demo@rapiddocs.io',
    username: 'demouser',
    full_name: 'Demo User',
    credits: 100,
    is_active: true,
    is_verified: true,
    created_at: new Date().toISOString()
  };

  private mockTokens: AuthTokens = {
    access_token: 'mock-access-token-' + Math.random().toString(36).substring(7),
    refresh_token: 'mock-refresh-token-' + Math.random().toString(36).substring(7),
    token_type: 'Bearer',
    expires_in: 3600
  };

  async register(data: any): Promise<AuthResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    // Create a new mock user with registration data
    const newUser: User = {
      ...this.mockUser,
      id: 'user-' + Math.random().toString(36).substring(7),
      email: data.email,
      username: data.username,
      full_name: data.full_name || data.username,
      created_at: new Date().toISOString()
    };

    const response: AuthResponse = {
      access_token: this.mockTokens.access_token,
      refresh_token: this.mockTokens.refresh_token,
      token_type: this.mockTokens.token_type
    };

    // Store in localStorage to simulate persistence
    localStorage.setItem('mock_user', JSON.stringify(newUser));
    localStorage.setItem('access_token', this.mockTokens.access_token);
    localStorage.setItem('refresh_token', this.mockTokens.refresh_token);

    console.log('Mock Registration:', response);
    return response;
  }

  async login(credentials: any): Promise<AuthResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    // Check if it's a demo account
    if (credentials.email === 'demo@rapiddocs.io' && credentials.password === 'demo123') {
      const response: AuthResponse = {
        access_token: this.mockTokens.access_token,
        refresh_token: this.mockTokens.refresh_token,
        token_type: this.mockTokens.token_type
      };

      localStorage.setItem('mock_user', JSON.stringify(this.mockUser));
      localStorage.setItem('access_token', this.mockTokens.access_token);
      localStorage.setItem('refresh_token', this.mockTokens.refresh_token);

      console.log('Mock Login Success:', response);
      return response;
    }

    // For any other credentials, check if user was previously registered
    const storedUser = localStorage.getItem('mock_user');
    if (storedUser) {
      const user = JSON.parse(storedUser);
      if (user.email === credentials.email) {
        const response: AuthResponse = {
          access_token: this.mockTokens.access_token,
          refresh_token: this.mockTokens.refresh_token,
          token_type: this.mockTokens.token_type
        };

        localStorage.setItem('access_token', this.mockTokens.access_token);
        localStorage.setItem('refresh_token', this.mockTokens.refresh_token);

        console.log('Mock Login Success:', response);
        return response;
      }
    }

    throw new Error('Invalid credentials. Use demo@rapiddocs.io / demo123 for demo access.');
  }

  async googleOAuth(): Promise<AuthResponse> {
    // Simulate OAuth flow
    await new Promise(resolve => setTimeout(resolve, 1000));

    const googleUser: User = {
      ...this.mockUser,
      id: 'google-' + Math.random().toString(36).substring(7),
      email: 'googleuser@gmail.com',
      username: 'googleuser',
      full_name: 'Google User'
    };

    const response: AuthResponse = {
      access_token: this.mockTokens.access_token,
      refresh_token: this.mockTokens.refresh_token,
      token_type: this.mockTokens.token_type
    };

    localStorage.setItem('mock_user', JSON.stringify(googleUser));
    localStorage.setItem('access_token', this.mockTokens.access_token);
    localStorage.setItem('refresh_token', this.mockTokens.refresh_token);

    console.log('Mock Google OAuth Success:', response);
    return response;
  }

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('mock_user');
    return userStr ? JSON.parse(userStr) : null;
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  logout(): void {
    localStorage.removeItem('mock_user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    console.log('Mock Logout');
  }
}

export const mockAuthService = new MockAuthService();