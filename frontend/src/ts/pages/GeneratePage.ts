import { router } from '../router';
import { authState } from '../auth/authState';
import { DocumentForm } from '../components/DocumentForm';

export class GeneratePage {
  render(): void {
    const app = document.getElementById('app');
    if (!app) return;

    app.innerHTML = `
      <div class="min-h-screen bg-gray-50 pt-20 pb-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <!-- Page Header -->
          <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">Generate Your Document</h1>
            <p class="text-xl text-gray-600">Create professional documents with AI in seconds</p>
          </div>

          <!-- Auth Warning (shown if not authenticated) -->
          ${!authState.isAuthenticated ? `
            <div class="mb-8 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm text-yellow-700">
                    <strong>Note:</strong> You can generate documents without logging in, but you'll need to <a href="/register" data-route="/register" class="font-semibold underline hover:text-yellow-800">create an account</a> to download them.
                  </p>
                </div>
              </div>
            </div>
          ` : ''}

          <!-- Document Generation Form Container -->
          <div class="bg-white rounded-lg shadow-md p-6 md:p-8">
            <form id="document-form" class="space-y-8">
              <!-- Document Description -->
              <div>
                <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
                  Document Description
                  <span class="text-red-500">*</span>
                </label>
                <textarea
                  id="description"
                  name="description"
                  rows="4"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  placeholder="Describe the document you want to generate. For example: 'Create a quarterly business report highlighting our company's growth in the tech sector, focusing on innovation and market expansion.'"
                  required
                ></textarea>
                <p class="mt-1 text-xs text-gray-500">Minimum 10 characters, maximum 2000 characters</p>
              </div>

              <!-- Document Length -->
              <div>
                <label for="length" class="block text-sm font-medium text-gray-700 mb-2">
                  Document Length (words)
                  <span class="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="length"
                  name="length"
                  min="500"
                  max="10000"
                  value="2000"
                  class="w-full md:w-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  required
                />
                <p class="mt-1 text-xs text-gray-500">Between 500 and 10,000 words</p>
              </div>

              <!-- Document Type -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-3">
                  Document Type
                  <span class="text-red-500">*</span>
                </label>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <!-- Formal Option -->
                  <label for="type-formal" class="relative flex cursor-pointer rounded-lg border border-gray-300 bg-white p-4 hover:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500 transition">
                    <input type="radio" id="type-formal" name="document_type" value="formal" class="sr-only peer" />
                    <span class="flex flex-1">
                      <span class="flex flex-col">
                        <span class="flex items-center gap-2 text-sm font-semibold text-gray-900">
                          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          Formal Document
                        </span>
                        <span class="mt-1 text-xs text-gray-500">Professional text-only document with decorative lines. No images or charts.</span>
                        <span class="mt-2 text-xs font-medium text-gray-600">⚡ ~60 seconds</span>
                      </span>
                    </span>
                    <svg class="h-5 w-5 text-blue-600 opacity-0 peer-checked:opacity-100 absolute top-4 right-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    <span class="pointer-events-none absolute -inset-px rounded-lg border-2 border-transparent peer-checked:border-blue-500"></span>
                  </label>

                  <!-- Infographic Option -->
                  <label for="type-infographic" class="relative flex cursor-pointer rounded-lg border border-gray-300 bg-white p-4 hover:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500 transition">
                    <input type="radio" id="type-infographic" name="document_type" value="infographic" class="sr-only peer" checked />
                    <span class="flex flex-1">
                      <span class="flex flex-col">
                        <span class="flex items-center gap-2 text-sm font-semibold text-gray-900">
                          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                          </svg>
                          Infographic Document
                        </span>
                        <span class="mt-1 text-xs text-gray-500">Rich visual document with AI images and data charts. Perfect for presentations.</span>
                        <span class="mt-2 text-xs font-medium text-gray-600">⏱️ ~120 seconds</span>
                      </span>
                    </span>
                    <svg class="h-5 w-5 text-blue-600 opacity-0 peer-checked:opacity-100 absolute top-4 right-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    <span class="pointer-events-none absolute -inset-px rounded-lg border-2 border-transparent peer-checked:border-blue-500"></span>
                  </label>
                </div>
                <p class="mt-2 text-xs text-gray-600">
                  <strong>Formal:</strong> Text + 3 decorative edge lines |
                  <strong>Infographic:</strong> Text + AI images + data charts
                </p>
              </div>

              <!-- Company Logo -->
              <div>
                <label for="logo-input" class="block text-sm font-medium text-gray-700 mb-2">Company Logo (Optional)</label>
                <div class="flex items-center gap-4">
                  <label for="logo-input" class="px-4 py-2 bg-gray-100 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-200 transition text-sm font-medium text-gray-700">
                    Choose File
                  </label>
                  <input type="file" id="logo-input" name="logo" accept="image/png,image/jpeg,image/svg+xml" class="hidden" />
                  <div id="file-preview" class="flex-1"></div>
                </div>
                <p class="mt-1 text-xs text-gray-500">PNG, JPG, or SVG. Max 5MB</p>
              </div>

              <!-- Watermark Option -->
              <div id="watermark-container" class="hidden">
                <div class="flex items-center gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <input type="checkbox" id="use-watermark" name="use_watermark" class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500" />
                  <label for="use-watermark" class="flex-1 cursor-pointer">
                    <span class="text-sm font-medium text-gray-900">Use logo as watermark</span>
                    <p class="text-xs text-gray-600 mt-1">Display your logo as a semi-transparent watermark on all pages (except cover)</p>
                  </label>
                </div>
              </div>

              <!-- Color Theme -->
              <div id="color-palette-container"></div>

              <!-- Statistics -->
              <div id="statistics-form-container"></div>

              <!-- Error Container -->
              <div id="error-container" class="hidden"></div>

              <!-- Submit Button -->
              <div class="flex justify-end">
                <button type="submit" id="submit-btn" class="btn-primary flex items-center gap-2">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Generate Document
                </button>
              </div>
            </form>

            <!-- Loading Container -->
            <div id="loading-container" class="hidden mt-8">
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div class="flex items-center mb-4">
                  <svg class="animate-spin h-5 w-5 text-blue-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <h3 class="text-lg font-semibold text-blue-800">Generating Your Document</h3>
                </div>
                <div class="mb-3">
                  <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div id="progress-bar" class="bg-blue-600 h-3 rounded-full transition-all duration-300" style="width: 0%"></div>
                  </div>
                </div>
                <p id="progress-text" class="text-sm text-gray-700 font-medium">0% - Initializing...</p>
                <p class="text-xs text-gray-600 mt-4">This may take 1-3 minutes depending on document complexity. Please don't close this page.</p>
              </div>
            </div>

            <!-- Result Container -->
            <div id="result-container" class="mt-8"></div>
          </div>

          <!-- Download Modal (shown after generation for non-authenticated users) -->
          <div id="auth-required-modal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div class="mt-3 text-center">
                <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
                  <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 class="text-lg leading-6 font-medium text-gray-900 mt-5">Document Generated!</h3>
                <div class="mt-2 px-7 py-3">
                  <p class="text-sm text-gray-500">
                    Your document has been generated successfully. Create an account to download it and save it to your library.
                  </p>
                </div>
                <div class="items-center px-4 py-3 space-y-3">
                  <button
                    id="modal-register-btn"
                    class="px-4 py-2 bg-blue-600 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    Create Account
                  </button>
                  <button
                    id="modal-login-btn"
                    class="px-4 py-2 bg-white text-gray-700 text-base font-medium rounded-md w-full border border-gray-300 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    I Have an Account
                  </button>
                  <button
                    id="modal-close-btn"
                    class="px-4 py-2 bg-white text-gray-500 text-sm font-medium rounded-md w-full hover:text-gray-700"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Initialize the document form
    try {
      new DocumentForm('document-form');
    } catch (error) {
      console.error('Failed to initialize document form:', error);
    }

    this.attachEventListeners();
    this.setupGenerationListener();
  }

  private attachEventListeners(): void {
    // Handle route navigation from warning message
    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      const link = target.closest('[data-route]') as HTMLAnchorElement;
      if (link) {
        e.preventDefault();
        const route = link.getAttribute('data-route');
        if (route) {
          router.navigate(route);
        }
      }
    });

    // Modal buttons
    const modalRegisterBtn = document.getElementById('modal-register-btn');
    const modalLoginBtn = document.getElementById('modal-login-btn');
    const modalCloseBtn = document.getElementById('modal-close-btn');

    if (modalRegisterBtn) {
      modalRegisterBtn.addEventListener('click', () => {
        router.navigate('/register');
      });
    }

    if (modalLoginBtn) {
      modalLoginBtn.addEventListener('click', () => {
        router.navigate('/login');
      });
    }

    if (modalCloseBtn) {
      modalCloseBtn.addEventListener('click', () => {
        this.hideAuthModal();
      });
    }
  }

  private setupGenerationListener(): void {
    // Listen for document generation completion
    // This would be triggered by the DocumentForm component
    window.addEventListener('document-generated', ((e: CustomEvent) => {
      // Document has been generated
      console.log('Document generated:', e.detail.documentId);

      // If user is not authenticated, show the auth modal
      if (!authState.isAuthenticated) {
        this.showAuthModal();
      } else {
        // If authenticated, allow download immediately
        // This would be handled by the DocumentForm component
      }
    }) as EventListener);
  }

  private showAuthModal(): void {
    const modal = document.getElementById('auth-required-modal');
    if (modal) {
      modal.classList.remove('hidden');
    }
  }

  private hideAuthModal(): void {
    const modal = document.getElementById('auth-required-modal');
    if (modal) {
      modal.classList.add('hidden');
    }
  }

  destroy(): void {
    // Cleanup if needed
    window.removeEventListener('document-generated', this.setupGenerationListener);
  }
}
