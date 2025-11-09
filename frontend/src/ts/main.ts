import '../styles/main.css';
import { router } from './router';
import { Navigation } from './components/Navigation';
import { authService } from './auth/authService';

// Setup axios interceptors for authentication
authService.setupAxiosInterceptors();

// Register routes
router.register('/', async () => {
  const { HomePage } = await import('./pages/HomePage');
  const page = new HomePage();
  page.render();
});

router.register('/generate', async () => {
  const { GeneratePage } = await import('./pages/GeneratePage');
  const page = new GeneratePage();
  page.render();
});

router.register('/login', async () => {
  const { LoginPage } = await import('./pages/LoginPage');
  const page = new LoginPage();
  page.render();
});

router.register('/register', async () => {
  const { RegisterPage } = await import('./pages/RegisterPage');
  const page = new RegisterPage();
  page.render();
});

router.register('/about/developer', async () => {
  const { AboutDeveloperPage } = await import('./pages/AboutDeveloperPage');
  const page = new AboutDeveloperPage();
  page.render();
});

router.register('/about/product', async () => {
  const { AboutProductPage } = await import('./pages/AboutProductPage');
  const page = new AboutProductPage();
  page.render();
});

router.register('/pricing', async () => {
  const { PricingPage } = await import('./pages/PricingPage');
  const page = new PricingPage();
  page.render();
});

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  console.log('DocGen initialized');

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
