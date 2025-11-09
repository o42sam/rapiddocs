import { authService, User } from './authService';

type AuthStateListener = (isAuthenticated: boolean, user: User | null) => void;

class AuthState {
  private listeners: Set<AuthStateListener> = new Set();
  private _isAuthenticated: boolean = false;
  private _user: User | null = null;

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    this._isAuthenticated = authService.isAuthenticated();
    this._user = authService.getUser();
  }

  get isAuthenticated(): boolean {
    return this._isAuthenticated;
  }

  get user(): User | null {
    return this._user;
  }

  subscribe(listener: AuthStateListener): () => void {
    this.listeners.add(listener);
    // Immediately call with current state
    listener(this._isAuthenticated, this._user);

    // Return unsubscribe function
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify(): void {
    this.listeners.forEach(listener => {
      listener(this._isAuthenticated, this._user);
    });
  }

  setAuthenticated(user: User): void {
    this._isAuthenticated = true;
    this._user = user;
    this.notify();
  }

  setUnauthenticated(): void {
    this._isAuthenticated = false;
    this._user = null;
    this.notify();
  }

  async refreshUser(): Promise<void> {
    if (this._isAuthenticated) {
      try {
        const user = await authService.getCurrentUser();
        this.setAuthenticated(user);
      } catch (error) {
        console.error('Failed to refresh user:', error);
        this.setUnauthenticated();
      }
    }
  }
}

export const authState = new AuthState();
