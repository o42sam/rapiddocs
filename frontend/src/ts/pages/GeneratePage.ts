import { router } from '../router';
import { authState } from '../auth/authState';
import { DocumentForm } from '../components/DocumentForm';

export class GeneratePage {
  private generatedDocumentId: string | null = null;

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
          <div class="bg-white rounded-lg shadow-md">
            <div id="document-form-container"></div>
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
    const formContainer = document.getElementById('document-form-container');
    if (formContainer) {
      // Use the existing DocumentForm component if it exists
      try {
        new DocumentForm('document-form-container');
      } catch (error) {
        console.error('Failed to initialize document form:', error);
        formContainer.innerHTML = `
          <div class="p-8 text-center text-red-600">
            Failed to load document form. Please refresh the page.
          </div>
        `;
      }
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
      const { documentId } = e.detail;
      this.generatedDocumentId = documentId;

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
