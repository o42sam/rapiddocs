import '../styles/main.css';
import { router } from './router';
import { Navigation } from './components/Navigation';
import { CreditsPurchaseModal } from './components/CreditsPurchaseModal';
import { authService } from './auth/authService';
import { googleOAuthService } from './auth/googleOAuthService';
import { MouseCursor } from './utils/mouseCursor';

// Setup axios interceptors for authentication
authService.setupAxiosInterceptors();

// Initialize credits purchase modal
new CreditsPurchaseModal();

// Initialize mouse cursor effect
new MouseCursor();

// Handle OAuth callback if present
if (googleOAuthService.isOAuthCallback()) {
  document.addEventListener('DOMContentLoaded', async () => {
    const app = document.getElementById('app');
    if (app) {
      app.innerHTML = `
        <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-purple-50">
          <div class="text-center">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
            <p class="text-gray-600">Completing sign in with Google...</p>
          </div>
        </div>
      `;
    }

    try {
      await googleOAuthService.handleCallback();

      // After successful callback handling, show success and redirect
      if (app) {
        app.innerHTML = `
          <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-purple-50">
            <div class="text-center">
              <div class="text-green-600 text-5xl mb-4">✓</div>
              <h2 class="text-2xl font-bold text-gray-900 mb-2">Sign In Successful!</h2>
              <p class="text-gray-600 mb-6">Redirecting to document generation...</p>
            </div>
          </div>
        `;
      }

      // Wait a moment before navigating to show success message
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Navigate to generate page (router will handle rendering)
      router.navigate('/generate');

    } catch (error) {
      console.error('OAuth callback error:', error);
      if (app) {
        app.innerHTML = `
          <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-purple-50 px-4">
            <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
              <div class="text-red-600 text-5xl mb-4">⚠️</div>
              <h2 class="text-2xl font-bold text-gray-900 mb-2">Sign In Failed</h2>
              <p class="text-gray-600 mb-6">${(error as Error).message || 'An error occurred during sign in'}</p>
              <button onclick="window.location.href='/login'" class="btn-primary">
                Back to Sign In
              </button>
            </div>
          </div>
        `;
      }
    }
  });
}

// Track current page for cleanup
let currentPage: any = null;

// Register routes
router.register('/', async () => {
  if (currentPage && currentPage.destroy) {
    currentPage.destroy();
  }
  const { HomePage } = await import('./pages/HomePage');
  const page = new HomePage();
  page.render();
  currentPage = page;
});

router.register('/generate', async () => {
  if (currentPage && currentPage.destroy) {
    currentPage.destroy();
  }
  const { GeneratePage } = await import('./pages/GeneratePage');
  const page = new GeneratePage();
  page.render();
  currentPage = page;
});

router.register('/login', async () => {
  if (currentPage && currentPage.destroy) {
    currentPage.destroy();
  }
  const { LoginPage } = await import('./pages/LoginPage');
  const page = new LoginPage();
  page.render();
  currentPage = page;
});

router.register('/register', async () => {
  if (currentPage && currentPage.destroy) {
    currentPage.destroy();
  }
  const { RegisterPage } = await import('./pages/RegisterPage');
  const page = new RegisterPage();
  page.render();
  currentPage = page;
});

router.register('/about/product', async () => {
  if (currentPage && currentPage.destroy) {
    currentPage.destroy();
  }
  const { AboutProductPage } = await import('./pages/AboutProductPage');
  const page = new AboutProductPage();
  page.render();
  currentPage = page;
});

router.register('/pricing', async () => {
  if (currentPage && currentPage.destroy) {
    currentPage.destroy();
  }
  const { PricingPage } = await import('./pages/PricingPage');
  const page = new PricingPage();
  page.render();
  currentPage = page;
});

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  console.log('RapidDocs initialized');

  // Create navigation
  const nav = new Navigation();
  const navContainer = document.getElementById('nav-container');
  if (navContainer) {
    nav.mount(navContainer);
  } else {
    // If nav-container doesn't exist, prepend to body
    document.body.insertBefore(nav.getElement(), document.body.firstChild);
  }
});
