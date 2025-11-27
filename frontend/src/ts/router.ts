/**
 * Simple client-side router
 */

import { loadingScreen } from './components/LoadingScreen';

type RouteHandler = () => void | Promise<void>;

interface Route {
  path: string;
  handler: RouteHandler;
  requiresAuth?: boolean;
}

class Router {
  private routes: Route[] = [];
  private currentPath: string = '/';
  private isInitialized: boolean = false;

  constructor() {
    window.addEventListener('popstate', () => this.handleRoute());
    window.addEventListener('DOMContentLoaded', () => {
      // Mount loading screen to DOM
      loadingScreen.mount();
      this.isInitialized = true;
      this.handleRoute();
    });
  }

  register(path: string, handler: RouteHandler, requiresAuth: boolean = false): void {
    this.routes.push({ path, handler, requiresAuth });
  }

  navigate(path: string): void {
    window.history.pushState({}, '', path);
    this.currentPath = path;
    this.handleRoute();
  }

  private async handleRoute(): Promise<void> {
    const path = window.location.pathname;
    this.currentPath = path;

    // Show loading screen if initialized
    if (this.isInitialized) {
      loadingScreen.show();
    }

    // Find matching route
    const route = this.routes.find(r => {
      if (r.path === path) return true;
      // Support dynamic routes like /generate/:id
      const routeParts = r.path.split('/');
      const pathParts = path.split('/');
      if (routeParts.length !== pathParts.length) return false;
      return routeParts.every((part, i) => part.startsWith(':') || part === pathParts[i]);
    });

    try {
      if (route) {
        // Check authentication
        if (route.requiresAuth) {
          const { authState } = await import('./auth/authState');
          if (!authState.isAuthenticated) {
            this.navigate('/login');
            return;
          }
        }

        // Execute route handler
        await route.handler();
      } else {
        // 404 - redirect to home
        this.navigate('/');
        return;
      }
    } finally {
      // Hide loading screen after route is handled
      // Add a small delay to ensure the page has rendered
      setTimeout(() => {
        if (this.isInitialized) {
          loadingScreen.hide();
        }
      }, 100);
    }
  }

  getCurrentPath(): string {
    return this.currentPath;
  }

  getParams(): Record<string, string> {
    const params: Record<string, string> = {};
    this.routes.find(r => {
      const routeParts = r.path.split('/');
      const pathParts = this.currentPath.split('/');
      if (routeParts.length !== pathParts.length) return false;
      return routeParts.every((part, i) => {
        if (part.startsWith(':')) {
          params[part.slice(1)] = pathParts[i];
          return true;
        }
        return part === pathParts[i];
      });
    });
    return params;
  }
}

export const router = new Router();

// Helper function to create navigation links
export function createLink(href: string, text: string, className: string = ''): HTMLAnchorElement {
  const link = document.createElement('a');
  link.href = href;
  link.textContent = text;
  link.className = className;

  link.addEventListener('click', (e) => {
    e.preventDefault();
    router.navigate(href);
  });

  return link;
}
