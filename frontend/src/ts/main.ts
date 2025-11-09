import '../styles/main.css';
import { router } from './router';
import { Navigation } from './components/Navigation';
import { authService } from './auth/authService';

// Setup axios interceptors for authentication
authService.setupAxiosInterceptors();

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

  // Initialize router
  router.init();
});
