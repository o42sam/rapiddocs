import { router, createLink } from '../router';
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
    authState.subscribe((isAuthenticated) => {
      this.render();
    });
  }

  private render(): void {
    const isAuthenticated = authState.isAuthenticated;
    const user = authState.user;

    this.element.className = 'fixed top-0 left-0 right-0 bg-white shadow-md z-50 nav-fade-in';
    this.element.innerHTML = `
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex-shrink-0">
            <a href="/" class="text-2xl font-bold gradient-primary bg-clip-text text-transparent hover:opacity-80 transition-opacity">
              DocGen
            </a>
          </div>

          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center space-x-8">
            <!-- About Menu -->
            <div class="relative group">
              <button class="text-gray-700 hover:text-blue-600 font-medium transition-colors flex items-center">
                About
                <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div class="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                <div class="py-1">
                  <a href="/" data-scroll="about-developer" class="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors">
                    Developer
                  </a>
                  <a href="/" data-scroll="about-product" class="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors">
                    Product
                  </a>
                </div>
              </div>
            </div>

            <a href="/" data-scroll="pricing" class="text-gray-700 hover:text-blue-600 font-medium transition-colors">
              Pricing
            </a>

            ${isAuthenticated ? `
              <a href="/generate" class="text-gray-700 hover:text-blue-600 font-medium transition-colors" data-route="/generate">
                Generate
              </a>
              <div class="relative group">
                <button class="text-gray-700 hover:text-blue-600 font-medium transition-colors flex items-center">
                  ${user?.username || 'Account'}
                  <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                <div class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                  <div class="py-1">
                    <a href="/profile" class="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors" data-route="/profile">
                      Profile
                    </a>
                    <button id="logout-btn" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors">
                      Logout
                    </button>
                  </div>
                </div>
              </div>
            ` : `
              <a href="/login" class="text-gray-700 hover:text-blue-600 font-medium transition-colors" data-route="/login">
                Log In
              </a>
              <a href="/register" class="btn-primary" data-route="/register">
                Get Started
              </a>
            `}
          </div>

          <!-- Mobile menu button -->
          <div class="md:hidden">
            <button id="mobile-menu-btn" class="text-gray-700 hover:text-blue-600 focus:outline-none">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Mobile menu -->
        <div id="mobile-menu" class="md:hidden ${this.mobileMenuOpen ? 'block slide-down' : 'hidden'}">
          <div class="px-2 pt-2 pb-3 space-y-1">
            <div class="space-y-1">
              <div class="text-gray-700 font-medium px-3 py-2">About</div>
              <a href="/" data-scroll="about-developer" class="block pl-6 pr-3 py-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors">
                Developer
              </a>
              <a href="/" data-scroll="about-product" class="block pl-6 pr-3 py-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors">
                Product
              </a>
            </div>

            <a href="/" data-scroll="pricing" class="block px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-md font-medium transition-colors">
              Pricing
            </a>

            ${isAuthenticated ? `
              <a href="/generate" class="block px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-md font-medium transition-colors" data-route="/generate">
                Generate
              </a>
              <a href="/profile" class="block px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-md font-medium transition-colors" data-route="/profile">
                Profile
              </a>
              <button id="mobile-logout-btn" class="block w-full text-left px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-md font-medium transition-colors">
                Logout
              </button>
            ` : `
              <a href="/login" class="block px-3 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-md font-medium transition-colors" data-route="/login">
                Log In
              </a>
              <a href="/register" class="block px-3 py-2 text-center bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 transition-colors" data-route="/register">
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
