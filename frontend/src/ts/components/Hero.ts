import { router } from '../router';

export class Hero {
  private element: HTMLElement;

  constructor() {
    this.element = document.createElement('section');
    this.render();
    this.attachEventListeners();
  }

  private render(): void {
    this.element.className = 'min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 pt-16';
    this.element.innerHTML = `
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div class="text-center max-w-4xl mx-auto">
          <!-- Main Heading -->
          <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 hero-title-fade">
            Transform Your Ideas Into
            <span class="block mt-2 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 bg-clip-text text-transparent font-extrabold">
              Professional Documents
            </span>
          </h1>

          <!-- Subheading -->
          <p class="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto hero-subtitle-fade">
            AI-powered document generation with stunning visualizations and custom branding.
            Create beautiful PDFs in seconds.
          </p>

          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center hero-button-fade">
            <button
              id="generate-now-btn"
              class="btn-primary w-full sm:w-auto"
            >
              Generate Document Now
              <svg class="w-5 h-5 ml-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>

            <a href="#features" class="btn-secondary w-full sm:w-auto">
              Learn More
            </a>
          </div>

          <!-- Features Grid -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20" data-animate>
            <div class="bg-white p-6 rounded-xl shadow-lg card-hover">
              <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Lightning Fast</h3>
              <p class="text-gray-600">Generate professional documents in seconds with AI</p>
            </div>

            <div class="bg-white p-6 rounded-xl shadow-lg card-hover">
              <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Custom Branding</h3>
              <p class="text-gray-600">Add your logo and choose your color scheme</p>
            </div>

            <div class="bg-white p-6 rounded-xl shadow-lg card-hover">
              <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Data Visualization</h3>
              <p class="text-gray-600">Beautiful charts and graphs automatically created</p>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  private attachEventListeners(): void {
    const generateBtn = this.element.querySelector('#generate-now-btn');
    if (generateBtn) {
      generateBtn.addEventListener('click', () => {
        router.navigate('/generate');
      });
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
