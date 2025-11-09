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
            <div class="flex items-center justify-center mb-4">
              <svg class="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            <div class="flex items-center justify-center mb-4">
              <svg class="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">About RapidDocs</h2>
            <p class="text-xl text-gray-600 max-w-2xl mx-auto">
              Learn more about our mission and technology
            </p>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <!-- About Developer -->
            <div id="about-developer" class="bg-white p-8 rounded-xl shadow-lg card-hover" data-animate>
              <div class="flex items-center mb-6">
                <div class="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mr-4">
                  <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                </div>
                <h3 class="text-2xl font-bold text-gray-900">About the Developer</h3>
              </div>

              <div class="space-y-4">
                <div class="flex items-start">
                  <svg class="w-6 h-6 text-blue-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  <p class="text-gray-600">
                    Built with passion by developers who understand the pain of creating professional documents manually.
                  </p>
                </div>

                <div class="flex items-start">
                  <svg class="w-6 h-6 text-purple-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <p class="text-gray-600">
                    We've leveraged cutting-edge AI technology to automate the entire document creation process.
                  </p>
                </div>

                <div class="flex items-start">
                  <svg class="w-6 h-6 text-indigo-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                  <p class="text-gray-600">
                    Our team combines expertise in machine learning, design, and document generation to deliver professional quality.
                  </p>
                </div>
              </div>
            </div>

            <!-- About Product -->
            <div id="about-product" class="bg-white p-8 rounded-xl shadow-lg card-hover" data-animate>
              <div class="flex items-center mb-6">
                <div class="w-14 h-14 bg-gradient-to-br from-green-500 to-teal-600 rounded-xl flex items-center justify-center mr-4">
                  <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 class="text-2xl font-bold text-gray-900">About the Product</h3>
              </div>

              <div class="space-y-4">
                <div class="flex items-start">
                  <svg class="w-6 h-6 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <p class="text-gray-600">
                    RapidDocs is an AI-powered document generation platform that transforms your ideas into professional PDFs.
                  </p>
                </div>

                <div class="flex items-start">
                  <svg class="w-6 h-6 text-teal-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                  </svg>
                  <p class="text-gray-600">
                    Features custom branding and automated data visualizations for a polished, professional look.
                  </p>
                </div>

                <div class="flex items-start">
                  <svg class="w-6 h-6 text-blue-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

  destroy(): void {
    this.hero.unmount();
  }
}
