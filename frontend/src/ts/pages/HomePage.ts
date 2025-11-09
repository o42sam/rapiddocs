import { Hero } from '../components/Hero';
import { initScrollAnimations } from '../utils/intersectionObserver';

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
            <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Powerful Features
            </h2>
            <p class="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to create professional documents
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            ${this.renderFeatureCard('AI-Powered Generation', 'Advanced AI creates comprehensive, well-structured documents based on your description', 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z', 'blue')}
            ${this.renderFeatureCard('Custom Branding', 'Upload your company logo and choose custom color schemes', 'M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01', 'purple')}
            ${this.renderFeatureCard('Data Visualization', 'Automatic chart generation for your statistics and metrics', 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', 'green')}
            ${this.renderFeatureCard('Multiple Document Types', 'Choose between formal reports or modern infographics', 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', 'red')}
            ${this.renderFeatureCard('High-Quality PDF', 'Professional PDFs ready for printing or sharing', 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12', 'indigo')}
            ${this.renderFeatureCard('Fast & Secure', 'Lightning-fast generation with enterprise-grade security', 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z', 'yellow')}
          </div>
        </div>
      </section>

      <!-- About Section -->
      <section id="about" class="py-20 bg-gray-50">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-16" data-animate>
            <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">About DocGen</h2>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <!-- About Developer -->
            <div id="about-developer" class="bg-white p-8 rounded-xl shadow-lg" data-animate>
              <h3 class="text-2xl font-bold text-gray-900 mb-4">About the Developer</h3>
              <p class="text-gray-600 mb-4">
                Built with passion by developers who understand the pain of creating professional documents manually.
                We've leveraged cutting-edge AI technology to automate the entire process.
              </p>
              <p class="text-gray-600">
                Our team combines expertise in machine learning, design, and document generation to deliver
                a product that saves you time while maintaining professional quality.
              </p>
            </div>

            <!-- About Product -->
            <div id="about-product" class="bg-white p-8 rounded-xl shadow-lg" data-animate>
              <h3 class="text-2xl font-bold text-gray-900 mb-4">About the Product</h3>
              <p class="text-gray-600 mb-4">
                DocGen is an AI-powered document generation platform that transforms your ideas into
                professional PDFs with custom branding and data visualizations.
              </p>
              <p class="text-gray-600">
                Whether you need business reports, marketing materials, or data-driven presentations,
                DocGen handles everything from content creation to final formatting.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Pricing Section -->
      <section id="pricing" class="py-20 bg-white">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-16" data-animate>
            <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Simple Pricing</h2>
            <p class="text-xl text-gray-600">Choose the plan that works for you</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            ${this.renderPricingCard('Free', '0', ['5 documents/month', 'Basic templates', 'Standard quality', 'Email support'], false)}
            ${this.renderPricingCard('Pro', '29', ['Unlimited documents', 'All templates', 'High quality', 'Priority support', 'Custom branding', 'API access'], true)}
            ${this.renderPricingCard('Enterprise', '99', ['Everything in Pro', 'Dedicated support', 'Custom integrations', 'SLA guarantee', 'Team management', 'Advanced analytics'], false)}
          </div>
        </div>
      </section>
    `;

    // Mount hero
    const heroContainer = document.getElementById('hero-container');
    if (heroContainer) {
      this.hero.mount(heroContainer);
    }

    // Initialize scroll animations
    initScrollAnimations();
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

  private renderPricingCard(name: string, price: string, features: string[], highlighted: boolean): string {
    return `
      <div class="bg-white rounded-xl shadow-lg ${highlighted ? 'ring-2 ring-blue-600 transform scale-105' : ''} p-8" data-animate>
        ${highlighted ? '<div class="text-center text-blue-600 font-semibold mb-4">MOST POPULAR</div>' : ''}
        <div class="text-center mb-8">
          <h3 class="text-2xl font-bold text-gray-900 mb-2">${name}</h3>
          <div class="text-5xl font-bold text-gray-900">
            $${price}
            <span class="text-lg text-gray-600">/mo</span>
          </div>
        </div>
        <ul class="space-y-4 mb-8">
          ${features.map(feature => `
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-gray-600">${feature}</span>
            </li>
          `).join('')}
        </ul>
        <button class="${highlighted ? 'btn-primary' : 'btn-outline text-blue-600'} w-full">
          Get Started
        </button>
      </div>
    `;
  }

  destroy(): void {
    this.hero.unmount();
  }
}
