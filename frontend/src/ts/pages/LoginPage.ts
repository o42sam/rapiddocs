import { router } from '../router';
import { authService } from '../auth/authService';
import { authState } from '../auth/authState';
import { GoogleSignInButton } from '../components/GoogleSignInButton';

export class LoginPage {
  private googleButton?: GoogleSignInButton;
  render(): void {
    const app = document.getElementById('app');
    if (!app) return;

    app.innerHTML = `
      <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-purple-50 pt-32 pb-12 px-4 sm:px-6 lg:px-8">
        <div class="max-w-md w-full space-y-8">
          <!-- Header -->
          <div class="text-center">
            <h2 class="text-4xl font-bold text-gray-900 mb-2">Welcome Back</h2>
            <p class="text-gray-600">Sign in to continue to RapidDocs</p>
          </div>

          <!-- Login Form -->
          <div class="bg-white rounded-xl shadow-lg p-8">
            <form id="login-form" class="space-y-6">
              <!-- Email -->
              <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  autocomplete="email"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition"
                  placeholder="you@example.com"
                />
              </div>

              <!-- Password -->
              <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  required
                  autocomplete="current-password"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition"
                  placeholder="Enter your password"
                />
              </div>

              <!-- Remember Me & Forgot Password -->
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label for="remember-me" class="ml-2 block text-sm text-gray-700">
                    Remember me
                  </label>
                </div>
                <a href="#" class="text-sm text-primary-600 hover:text-primary-700 font-medium">
                  Forgot password?
                </a>
              </div>

              <!-- Error Message -->
              <div id="error-message" class="hidden bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                id="login-btn"
                class="w-full btn-primary flex items-center justify-center"
              >
                <span id="login-btn-text">Sign In</span>
                <svg id="login-spinner" class="hidden animate-spin ml-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </button>
            </form>

            <!-- Divider -->
            <div class="mt-6">
              <div class="relative">
                <div class="absolute inset-0 flex items-center">
                  <div class="w-full border-t border-gray-300"></div>
                </div>
                <div class="relative flex justify-center text-sm">
                  <span class="px-2 bg-white text-gray-500">Or continue with</span>
                </div>
              </div>
            </div>

            <!-- Google Sign In -->
            <div id="google-signin-container" class="mt-6">
              <!-- Google button will be inserted here -->
            </div>

            <!-- Divider -->
            <div class="mt-6">
              <div class="relative">
                <div class="absolute inset-0 flex items-center">
                  <div class="w-full border-t border-gray-300"></div>
                </div>
                <div class="relative flex justify-center text-sm">
                  <span class="px-2 bg-white text-gray-500">Don't have an account?</span>
                </div>
              </div>
            </div>

            <!-- Register Link -->
            <div class="mt-6">
              <button
                id="register-link"
                class="w-full btn-secondary"
              >
                Create Account
              </button>
            </div>
          </div>
        </div>
      </div>
    `;

    this.attachEventListeners();
  }

  private attachEventListeners(): void {
    const form = document.getElementById('login-form') as HTMLFormElement;
    const registerLink = document.getElementById('register-link');

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleLogin(form);
      });
    }

    if (registerLink) {
      registerLink.addEventListener('click', (e) => {
        e.preventDefault();
        router.navigate('/register');
      });
    }

    // Add Google Sign-In button
    this.setupGoogleSignIn();
  }

  private setupGoogleSignIn(): void {
    const container = document.getElementById('google-signin-container');
    if (!container) return;

    // Create Google button with error handler
    this.googleButton = new GoogleSignInButton('Sign in with Google', (error) => {
      const errorMessage = document.getElementById('error-message');
      if (errorMessage) {
        errorMessage.textContent = error.message || 'Failed to sign in with Google';
        errorMessage.classList.remove('hidden');
      }
    });

    // Insert button HTML
    container.innerHTML = this.googleButton.getHTML();

    // Attach event listener
    const button = container.querySelector('.google-signin-btn') as HTMLButtonElement;
    if (button) {
      this.googleButton.attachEventListener(button);
    }
  }

  private async handleLogin(form: HTMLFormElement): Promise<void> {
    const emailInput = form.querySelector('#email') as HTMLInputElement;
    const passwordInput = form.querySelector('#password') as HTMLInputElement;
    const submitBtn = document.getElementById('login-btn') as HTMLButtonElement;
    const btnText = document.getElementById('login-btn-text');
    const spinner = document.getElementById('login-spinner');
    const errorMessage = document.getElementById('error-message');

    if (!emailInput || !passwordInput) return;

    // Show loading state
    submitBtn.disabled = true;
    if (btnText) btnText.textContent = 'Signing in...';
    spinner?.classList.remove('hidden');
    errorMessage?.classList.add('hidden');

    try {
      await authService.login({
        email: emailInput.value,
        password: passwordInput.value
      });

      // Get user data after successful login
      const user = await authService.getCurrentUser();

      // Set authenticated state
      authState.setAuthenticated(user);

      // Small delay to ensure state propagates before navigation
      await new Promise(resolve => setTimeout(resolve, 50));

      // Redirect to generate page or home
      router.navigate('/generate');
    } catch (error: any) {
      // Show error message
      if (errorMessage) {
        errorMessage.textContent = error.response?.data?.detail || 'Invalid email or password. Please try again.';
        errorMessage.classList.remove('hidden');
      }
    } finally {
      // Reset loading state
      submitBtn.disabled = false;
      if (btnText) btnText.textContent = 'Sign In';
      spinner?.classList.add('hidden');
    }
  }
}
