import { Hero } from '../components/Hero';
import { initScrollAnimations } from '../utils/intersectionObserver';
import { router } from '../router';

export class HomePage {
  private hero: Hero;

  constructor() {
    this.hero = new Hero();
  }

  render(): void {
    const app = document.getElementById('app');
    if (!app) return;

    app.innerHTML = `
      <div id="hero-container"></div>

      <!-- Features Section -->
      <section id="features" class="py-20 bg-white">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-16" data-animate>
            <div class="flex items-center justify-center mb-4">
              <svg class="w-12 h-12 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </div>
            <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Powerful Features
            </h2>
            <p class="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to create professional documents
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            ${this.renderFeatureCard('AI-Powered Generation', 'Advanced AI creates comprehensive, well-structured documents based on your description', 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z', 'primary')}
            ${this.renderFeatureCard('Custom Branding', 'Upload your company logo and choose custom color schemes', 'M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01', 'primary')}
            ${this.renderFeatureCard('Data Visualization', 'Automatic chart generation for your statistics and metrics', 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', 'primary')}
            ${this.renderFeatureCard('Multiple Document Types', 'Choose between formal reports or modern infographics', 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', 'primary')}
            ${this.renderFeatureCard('High-Quality PDF', 'Professional PDFs ready for printing or sharing', 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12', 'primary')}
            ${this.renderFeatureCard('Fast & Secure', 'Lightning-fast generation with enterprise-grade security', 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z', 'primary')}
          </div>
        </div>
      </section>

      <!-- About Section -->
      <section id="about" class="py-20 bg-gray-50">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-16" data-animate>
            <div class="flex items-center justify-center mb-4">
              <svg class="w-12 h-12 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">About RapidDocs</h2>
            <p class="text-xl text-gray-600 max-w-2xl mx-auto">
              Learn more about our mission and technology
            </p>
          </div>

          <div class="max-w-3xl mx-auto">
            <!-- About Product -->
            <div id="about-product" class="bg-white p-8 rounded-xl shadow-lg card-hover" data-animate>
              <div class="flex items-center mb-6">
                <div class="w-14 h-14 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center mr-4">
                  <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 class="text-2xl font-bold text-gray-900">About the Product</h3>
              </div>

              <div class="space-y-4">
                <div class="flex items-start">
                  <svg class="w-6 h-6 text-primary-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <p class="text-gray-600">
                    RapidDocs is an AI-powered document generation platform that transforms your ideas into professional PDFs.
                  </p>
                </div>

                <div class="flex items-start">
                  <svg class="w-6 h-6 text-primary-600 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                  </svg>
                  <p class="text-gray-600">
                    Features custom branding and automated data visualizations for a polished, professional look.
                  </p>
                </div>

                <div class="flex items-start">
                  <svg class="w-6 h-6 text-primary-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p class="text-gray-600">
                    Perfect for business reports, marketing materials, or data-driven presentations with complete formatting control.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Footer -->
      <footer class="bg-gray-900 text-gray-300">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
            <!-- Brand Column -->
            <div class="md:col-span-1">
              <div class="flex items-center mb-4">
                <img src="/rd-logo.svg" alt="RapidDocs Logo" class="h-10 w-auto mr-2">
                <span class="text-xl font-bold text-white">RapidDocs</span>
              </div>
              <p class="text-gray-400 text-sm mb-4">
                Transform your ideas into professional documents with AI-powered generation.
              </p>
              <div class="flex space-x-4">
                <a href="#" class="text-gray-400 hover:text-white transition-colors">
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fill-rule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clip-rule="evenodd" />
                  </svg>
                </a>
                <a href="#" class="text-gray-400 hover:text-white transition-colors">
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </a>
                <a href="#" class="text-gray-400 hover:text-white transition-colors">
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
                  </svg>
                </a>
                <a href="#" class="text-gray-400 hover:text-white transition-colors">
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fill-rule="evenodd" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10c5.51 0 10-4.48 10-10S17.51 2 12 2zm6.605 4.61a8.502 8.502 0 011.93 5.314c-.281-.054-3.101-.629-5.943-.271-.065-.141-.12-.293-.184-.445a25.416 25.416 0 00-.564-1.236c3.145-1.28 4.577-3.124 4.761-3.362zM12 3.475c2.17 0 4.154.813 5.662 2.148-.152.216-1.443 1.941-4.48 3.08-1.399-2.57-2.95-4.675-3.189-5A8.687 8.687 0 0112 3.475zm-3.633.803a53.896 53.896 0 013.167 4.935c-3.992 1.063-7.517 1.04-7.896 1.04a8.581 8.581 0 014.729-5.975zM3.453 12.01v-.26c.37.01 4.512.065 8.775-1.215.25.477.477.965.694 1.453-.109.033-.228.065-.336.098-4.404 1.42-6.747 5.303-6.942 5.629a8.522 8.522 0 01-2.19-5.705zM12 20.547a8.482 8.482 0 01-5.239-1.8c.152-.315 1.888-3.656 6.703-5.337.022-.01.033-.01.054-.022a35.318 35.318 0 011.823 6.475 8.4 8.4 0 01-3.341.684zm4.761-1.465c-.086-.52-.542-3.015-1.659-6.084 2.679-.423 5.022.271 5.314.369a8.468 8.468 0 01-3.655 5.715z" clip-rule="evenodd" />
                  </svg>
                </a>
              </div>
            </div>

            <!-- Product Column -->
            <div>
              <h4 class="text-white font-semibold mb-4">Product</h4>
              <ul class="space-y-2">
                <li><a href="#features" class="text-sm hover:text-white transition-colors">Features</a></li>
                <li><a href="/pricing" class="text-sm hover:text-white transition-colors">Pricing</a></li>
                <li><a href="/generate" class="text-sm hover:text-white transition-colors">Generate Document</a></li>
                <li><a href="#" class="text-sm hover:text-white transition-colors">API Documentation</a></li>
              </ul>
            </div>

            <!-- Company Column -->
            <div>
              <h4 class="text-white font-semibold mb-4">Company</h4>
              <ul class="space-y-2">
                <li><a href="/" data-scroll="about-product" class="text-sm hover:text-white transition-colors">About</a></li>
                <li><a href="#" class="text-sm hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" class="text-sm hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>

            <!-- Legal Column -->
            <div>
              <h4 class="text-white font-semibold mb-4">Legal</h4>
              <ul class="space-y-2">
                <li><a href="/privacy-policy" class="text-sm hover:text-white transition-colors footer-link">Privacy Policy</a></li>
                <li><a href="/terms-of-service" class="text-sm hover:text-white transition-colors footer-link">Terms of Service</a></li>
                <li><a href="#" class="text-sm hover:text-white transition-colors">Cookie Policy</a></li>
                <li><a href="#" class="text-sm hover:text-white transition-colors">GDPR</a></li>
              </ul>
            </div>
          </div>

          <!-- Bottom Bar -->
          <div class="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p class="text-sm text-gray-400">
              &copy; 2025 RapidDocs. All rights reserved.
            </p>
            <div class="flex space-x-6 mt-4 md:mt-0">
              <a href="#" class="text-sm text-gray-400 hover:text-white transition-colors">Status</a>
              <a href="#" class="text-sm text-gray-400 hover:text-white transition-colors">Support</a>
              <a href="#" class="text-sm text-gray-400 hover:text-white transition-colors">Documentation</a>
            </div>
          </div>
        </div>
      </footer>
    `;

    // Mount hero
    const heroContainer = document.getElementById('hero-container');
    if (heroContainer) {
      this.hero.mount(heroContainer);
    }

    // Initialize scroll animations
    initScrollAnimations();

    // Add click handlers for footer legal links
    this.attachFooterLinkHandlers();
  }

  private attachFooterLinkHandlers(): void {
    const footerLinks = document.querySelectorAll('.footer-link');
    footerLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const href = (e.currentTarget as HTMLAnchorElement).getAttribute('href');
        if (href) {
          router.navigate(href);
        }
      });
    });
  }

  private renderFeatureCard(title: string, description: string, iconPath: string, color: string): string {
    return `
      <div class="bg-white p-6 rounded-xl shadow-lg card-hover" data-animate>
        <div class="w-12 h-12 bg-${color}-100 rounded-lg flex items-center justify-center mb-4">
          <svg class="w-6 h-6 text-${color}-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${iconPath}" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">${title}</h3>
        <p class="text-gray-600">${description}</p>
      </div>
    `;
  }

  destroy(): void {
    this.hero.unmount();
  }
}
