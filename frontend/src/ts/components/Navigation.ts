import { router } from '../router';
import { authState } from '../auth/authState';
import { authService } from '../auth/authService';

export class Navigation {
  private element: HTMLElement;
  private mobileMenuOpen: boolean = false;

  constructor() {
    this.element = document.createElement('nav');
    this.render();
    this.attachEventListeners();

    // Subscribe to auth state changes
    authState.subscribe(() => {
      this.render();
    });
  }

  private render(): void {
    const isAuthenticated = authState.isAuthenticated;
    const user = authState.user;

    this.element.className = 'fixed top-0 left-0 right-0 bg-gray-50 shadow-md z-50 nav-fade-in';
    this.element.innerHTML = `
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex-shrink-0">
            <a href="/" class="flex items-center hover:opacity-80 transition-opacity" data-route="/">
              <img src="/rd-logo.svg" alt="RapidDocs" class="h-12 w-auto logo-slide-in" />
              <span class="ml-3 text-2xl font-bold text-primary-800 logo-text-fade-in">RapidDocs</span>
            </a>
          </div>

          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center space-x-8">
            <a href="/" data-scroll="about-product" class="text-gray-700 hover:text-primary-600 font-medium transition-colors">
              About
            </a>

            ${isAuthenticated ? `
              <a href="/generate" class="text-gray-700 hover:text-primary-600 font-medium transition-colors" data-route="/generate">
                Generate
              </a>

              <!-- Credits Display -->
              <div class="relative group">
                <button class="flex items-center space-x-2 text-gray-700 hover:text-primary-600 font-medium transition-colors">
                  <svg class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd" />
                  </svg>
                  <span class="font-semibold">${user?.credits ?? 0}</span>
                </button>
                <div class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                  <div class="py-1">
                    <button id="buy-credits-btn" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-colors">
                      Buy Credits
                    </button>
                  </div>
                </div>
              </div>

              <!-- User Menu -->
              <div class="relative group">
                <button class="text-gray-700 hover:text-primary-600 font-medium transition-colors flex items-center">
                  ${user?.username || 'Account'}
                  <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                <div class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                  <div class="py-1">
                    <a href="/profile" class="block px-4 py-2 text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-colors" data-route="/profile">
                      Profile
                    </a>
                    <button id="logout-btn" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-colors">
                      Logout
                    </button>
                  </div>
                </div>
              </div>
            ` : `
              <a href="/login" class="text-gray-700 hover:text-primary-600 font-medium transition-colors" data-route="/login">
                Log In
              </a>
              <a href="/register" class="btn-primary" data-route="/register">
                Get Started
              </a>
            `}
          </div>

          <!-- Mobile menu button -->
          <div class="md:hidden">
            <button id="mobile-menu-btn" class="text-gray-700 hover:text-primary-600 focus:outline-none">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Mobile menu -->
        <div id="mobile-menu" class="md:hidden ${this.mobileMenuOpen ? 'block slide-down' : 'hidden'}">
          <div class="px-2 pt-2 pb-3 space-y-1">
            <a href="/" data-scroll="about-product" class="block px-3 py-2 text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-md font-medium transition-colors">
              About
            </a>

            ${isAuthenticated ? `
              <div class="flex items-center justify-between px-3 py-2 text-gray-700 font-medium">
                <span>Credits:</span>
                <span class="flex items-center space-x-1">
                  <svg class="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd" />
                  </svg>
                  <span class="font-semibold">${user?.credits ?? 0}</span>
                </span>
              </div>
              <button id="mobile-buy-credits-btn" class="block w-full text-left px-3 py-2 text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-md font-medium transition-colors">
                Buy Credits
              </button>
              <a href="/generate" class="block px-3 py-2 text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-md font-medium transition-colors" data-route="/generate">
                Generate
              </a>
              <a href="/profile" class="block px-3 py-2 text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-md font-medium transition-colors" data-route="/profile">
                Profile
              </a>
              <button id="mobile-logout-btn" class="block w-full text-left px-3 py-2 text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-md font-medium transition-colors">
                Logout
              </button>
            ` : `
              <a href="/login" class="block px-3 py-2 text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-md font-medium transition-colors" data-route="/login">
                Log In
              </a>
              <a href="/register" class="block px-3 py-2 text-center bg-primary-600 text-white rounded-md font-medium hover:bg-primary-700 transition-colors" data-route="/register">
                Get Started
              </a>
            `}
          </div>
        </div>
      </div>
    `;
  }

  private attachEventListeners(): void {
    // Mobile menu toggle
    this.element.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;

      // Mobile menu button
      if (target.id === 'mobile-menu-btn' || target.closest('#mobile-menu-btn')) {
        e.preventDefault();
        this.toggleMobileMenu();
      }

      // Buy Credits button
      if (target.id === 'buy-credits-btn' || target.id === 'mobile-buy-credits-btn') {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('open-credits-modal'));
      }

      // Logout buttons
      if (target.id === 'logout-btn' || target.id === 'mobile-logout-btn') {
        e.preventDefault();
        this.handleLogout();
      }

      // Scroll navigation
      const scrollLink = target.closest('[data-scroll]') as HTMLAnchorElement;
      if (scrollLink) {
        e.preventDefault();
        const sectionId = scrollLink.getAttribute('data-scroll');
        if (sectionId) {
          // Navigate to home page first if not already there
          if (window.location.pathname !== '/') {
            router.navigate('/');
            // Wait for page to load then scroll
            setTimeout(() => this.scrollToSection(sectionId), 100);
          } else {
            this.scrollToSection(sectionId);
          }
        }
        if (this.mobileMenuOpen) {
          this.toggleMobileMenu();
        }
        return;
      }

      // Route navigation
      const link = target.closest('[data-route]') as HTMLAnchorElement;
      if (link) {
        e.preventDefault();
        const route = link.getAttribute('data-route') || link.getAttribute('href') || '/';
        router.navigate(route);
        if (this.mobileMenuOpen) {
          this.toggleMobileMenu();
        }
      }
    });

    // Close mobile menu on window resize
    window.addEventListener('resize', () => {
      if (window.innerWidth >= 768 && this.mobileMenuOpen) {
        this.toggleMobileMenu();
      }
    });
  }

  private toggleMobileMenu(): void {
    this.mobileMenuOpen = !this.mobileMenuOpen;
    const mobileMenu = this.element.querySelector('#mobile-menu');
    if (mobileMenu) {
      if (this.mobileMenuOpen) {
        mobileMenu.classList.remove('hidden');
        mobileMenu.classList.add('slide-down');
      } else {
        mobileMenu.classList.add('hidden');
        mobileMenu.classList.remove('slide-down');
      }
    }
  }

  private scrollToSection(sectionId: string): void {
    const section = document.getElementById(sectionId);
    if (section) {
      const navHeight = this.element.offsetHeight;
      const sectionTop = section.offsetTop - navHeight - 20;
      window.scrollTo({
        top: sectionTop,
        behavior: 'smooth'
      });
    }
  }

  private async handleLogout(): Promise<void> {
    try {
      await authService.logout();
      authState.setUnauthenticated();
      router.navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }

  mount(parent: HTMLElement): void {
    parent.appendChild(this.element);
  }

  unmount(): void {
    this.element.remove();
  }

  getElement(): HTMLElement {
    return this.element;
  }
}
