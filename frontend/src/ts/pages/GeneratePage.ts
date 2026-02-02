import { router } from '../router';
import { authState } from '../auth/authState';
import { DocumentForm } from '../components/DocumentForm';

export class GeneratePage {
  render(): void {
    const app = document.getElementById('app');
    if (!app) return;

    // Show navigation
    const navContainer = document.getElementById('nav-container');
    if (navContainer) {
      navContainer.style.display = '';
    }

    app.innerHTML = `
      <div class="min-h-screen bg-gray-50 pb-12 pt-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <!-- Page Header -->
          <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">Generate Your Document</h1>
            <p class="text-xl text-gray-600">Create professional documents with AI in seconds</p>
          </div>

          <!-- Auth Warning (shown if not authenticated) -->
          ${!authState.isAuthenticated ? `
            <div class="mb-8 bg-primary-50 border-l-4 border-primary-400 p-4 rounded-lg">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm text-primary-700">
                    <strong>Please log in to generate documents.</strong> You'll be redirected to the login page when you click "Generate Document". Don't have an account? <a href="/register" data-route="/register" class="font-semibold underline hover:text-primary-800">Sign up here</a>.
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
                  rows="5"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition"
                  placeholder="Describe your document..."
                  required
                ></textarea>
                <div id="description-guide" class="mt-2 p-3 bg-primary-50 border border-primary-200 rounded-lg">
                  <p class="text-xs text-primary-900 font-medium mb-1">💡 Tips for best results:</p>
                  <p id="description-guide-text" class="text-xs text-primary-800 leading-relaxed"></p>
                </div>
                <p class="mt-2 text-xs text-gray-500">Minimum 10 characters, maximum 2000 characters</p>
              </div>

              <!-- Document Length -->
              <div id="length-container">
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
                  class="w-full md:w-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition"
                  required
                />
                <p class="mt-1 text-xs text-gray-500">Between 500 and 10,000 words</p>
              </div>

              <!-- Document Type -->
              <div>
                <label for="document-type-select" class="block text-sm font-medium text-gray-700 mb-2">
                  Document Type
                  <span class="text-red-500">*</span>
                </label>
                <select
                  id="document-type-select"
                  name="document_type"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition bg-white"
                  required
                >
                  <option value="formal">Formal Document - Text with decorative lines (⚡ ~60s, 34 credits)</option>
                  <option value="infographic" selected>Infographic Document - Text + AI images + charts (⏱️ ~120s, 52 credits)</option>
                  <option value="invoice">Invoice - Professional invoice with line items and totals (⚡ ~45s, 28 credits)</option>
                </select>
                <p class="mt-2 text-xs text-gray-600">
                  <strong>Formal:</strong> Professional text with decorative elements |
                  <strong>Infographic:</strong> Visual document with AI images and data charts |
                  <strong>Invoice:</strong> Structured billing document with itemized costs
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
                <div class="flex items-center gap-3 p-4 bg-primary-50 border border-primary-200 rounded-lg">
                  <input type="checkbox" id="use-watermark" name="use_watermark" class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-2 focus:ring-primary-500" />
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

              <!-- Insufficient Credits Warning -->
              <div id="insufficient-credits-warning" class="hidden bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div class="flex items-start">
                  <svg class="w-5 h-5 text-red-600 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                  <div class="flex-1">
                    <h3 class="text-sm font-medium text-red-800">Insufficient Credits</h3>
                    <p class="text-sm text-red-700 mt-1">
                      You don't have enough credits to generate this document. Please purchase more credits to continue.
                    </p>
                    <button
                      id="buy-credits-from-warning-btn"
                      class="mt-3 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700 transition-colors"
                    >
                      Buy Credits Now
                    </button>
                  </div>
                </div>
              </div>

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
              <div class="bg-primary-50 border border-primary-200 rounded-lg p-6">
                <div class="flex items-center mb-4">
                  <svg class="animate-spin h-5 w-5 text-primary-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <h3 class="text-lg font-semibold text-primary-800">Generating Your Document</h3>
                </div>
                <div class="mb-3">
                  <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div id="progress-bar" class="bg-primary-600 h-3 rounded-full transition-all duration-300" style="width: 0%"></div>
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
                <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-primary-100">
                  <svg class="h-6 w-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                    class="px-4 py-2 bg-primary-600 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
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

          <!-- No Logo Modal -->
          <div id="no-logo-modal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
              <div class="mt-3">
                <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
                  <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <h3 class="text-lg leading-6 font-medium text-gray-900 mt-4 text-center">No Logo Uploaded</h3>
                <div class="mt-3 px-4 py-3">
                  <p class="text-sm text-gray-600 text-center">
                    You haven't uploaded a company logo yet. Documents with business logos appear more professional and strengthen your brand identity.
                  </p>
                  <p class="text-sm text-gray-600 text-center mt-3">
                    Would you like to go back and add a logo, or continue without one?
                  </p>
                </div>
                <div class="items-center px-4 py-3 space-y-2">
                  <button
                    id="modal-add-logo-btn"
                    class="px-4 py-2 bg-primary-600 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors"
                  >
                    Add Logo
                  </button>
                  <button
                    id="modal-continue-without-logo-btn"
                    class="px-4 py-2 bg-white text-gray-700 text-base font-medium rounded-md w-full border border-gray-300 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
                  >
                    Continue Without Logo
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
    this.restoreFormData();
    this.setupCreditsCheck();
    this.setupDescriptionGuide();
    this.setupWatermarkToggle();
    this.setupLengthVisibility();
  }

  private attachEventListeners(): void {
    // Buy Credits button in warning
    const buyCreditsBtn = document.getElementById('buy-credits-from-warning-btn');
    if (buyCreditsBtn) {
      buyCreditsBtn.addEventListener('click', () => {
        window.dispatchEvent(new CustomEvent('open-credits-modal'));
      });
    }

    // Intercept form submission for unauthenticated users and logo check
    const form = document.getElementById('document-form') as HTMLFormElement;
    if (form) {
      form.addEventListener('submit', (e) => {
        // Check authentication first
        if (!authState.isAuthenticated) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();

          // Save form data before redirecting
          this.saveFormData();

          router.navigate('/login');
          return false;
        }

        // Check if logo is required for document type
        const documentTypeSelect = document.getElementById('document-type-select') as HTMLSelectElement;
        const logoInput = document.getElementById('logo-input') as HTMLInputElement;
        const documentType = documentTypeSelect?.value;
        const hasLogo = !!(logoInput?.files && logoInput.files.length > 0);
        const supportsWatermark = documentType === 'formal' || documentType === 'invoice';

        // Show modal if document supports watermark but no logo uploaded
        if (supportsWatermark && !hasLogo) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();

          this.showNoLogoModal();
          return false;
        }
      }, true); // Use capture phase to intercept before DocumentForm
    }

    // Auto-save form data on input changes
    if (form) {
      form.addEventListener('input', () => {
        if (!authState.isAuthenticated) {
          this.saveFormData();
        }
      });

      form.addEventListener('change', () => {
        if (!authState.isAuthenticated) {
          this.saveFormData();
        }
      });
    }

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

    // No Logo Modal buttons
    const modalAddLogoBtn = document.getElementById('modal-add-logo-btn');
    const modalContinueWithoutLogoBtn = document.getElementById('modal-continue-without-logo-btn');

    if (modalAddLogoBtn) {
      modalAddLogoBtn.addEventListener('click', () => {
        this.hideNoLogoModal();
        this.scrollToAndHighlightLogo();
      });
    }

    if (modalContinueWithoutLogoBtn) {
      modalContinueWithoutLogoBtn.addEventListener('click', () => {
        this.hideNoLogoModal();
        this.proceedWithGeneration();
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

  private showNoLogoModal(): void {
    const modal = document.getElementById('no-logo-modal');
    if (modal) {
      modal.classList.remove('hidden');
    }
  }

  private hideNoLogoModal(): void {
    const modal = document.getElementById('no-logo-modal');
    if (modal) {
      modal.classList.add('hidden');
    }
  }

  private scrollToAndHighlightLogo(): void {
    const logoSection = document.getElementById('logo-input')?.parentElement?.parentElement;
    if (logoSection) {
      // Scroll to logo section with smooth behavior
      logoSection.scrollIntoView({ behavior: 'smooth', block: 'center' });

      // Add halo effect with animation
      const haloClass = 'animate-halo';

      // Add inline styles for the animation
      const style = document.createElement('style');
      style.textContent = `
        @keyframes halo-pulse {
          0%, 100% {
            box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
            border-color: #3b82f6;
          }
          50% {
            box-shadow: 0 0 0 15px rgba(59, 130, 246, 0);
            border-color: #60a5fa;
          }
        }
        .animate-halo {
          animation: halo-pulse 2s ease-in-out 3;
          border: 2px solid #3b82f6;
          border-radius: 0.5rem;
          padding: 1rem;
          transition: all 0.3s ease;
        }
      `;

      if (!document.getElementById('halo-animation-style')) {
        style.id = 'halo-animation-style';
        document.head.appendChild(style);
      }

      // Apply the animation
      logoSection.classList.add(haloClass);

      // Remove the animation after it completes (2s * 3 iterations = 6s)
      setTimeout(() => {
        logoSection.classList.remove(haloClass);
      }, 6000);
    }
  }

  private proceedWithGeneration(): void {
    // Trigger form submission programmatically
    const form = document.getElementById('document-form') as HTMLFormElement;
    if (form) {
      // Create and dispatch a submit event
      const submitEvent = new Event('submit', {
        bubbles: true,
        cancelable: true
      });
      form.dispatchEvent(submitEvent);
    }
  }

  private saveFormData(): void {
    const form = document.getElementById('document-form') as HTMLFormElement;
    if (!form) return;

    const formData: any = {
      description: (document.getElementById('description') as HTMLTextAreaElement)?.value || '',
      length: (document.getElementById('length') as HTMLInputElement)?.value || '2000',
      documentType: (document.getElementById('document-type-select') as HTMLSelectElement)?.value || 'infographic',
      useWatermark: (document.getElementById('use-watermark') as HTMLInputElement)?.checked || false,
    };

    // Save to sessionStorage
    sessionStorage.setItem('generate_form_data', JSON.stringify(formData));
    console.log('Form data saved to sessionStorage');
  }

  private restoreFormData(): void {
    // Only restore if user just logged in
    const savedData = sessionStorage.getItem('generate_form_data');
    if (!savedData) return;

    try {
      const formData = JSON.parse(savedData);
      console.log('Restoring form data:', formData);

      // Restore description
      const descriptionField = document.getElementById('description') as HTMLTextAreaElement;
      if (descriptionField && formData.description) {
        descriptionField.value = formData.description;
      }

      // Restore length
      const lengthField = document.getElementById('length') as HTMLInputElement;
      if (lengthField && formData.length) {
        lengthField.value = formData.length;
      }

      // Restore document type
      if (formData.documentType) {
        const typeSelect = document.getElementById('document-type-select') as HTMLSelectElement;
        if (typeSelect) {
          typeSelect.value = formData.documentType;
        }
      }

      // Restore watermark checkbox
      const watermarkCheckbox = document.getElementById('use-watermark') as HTMLInputElement;
      if (watermarkCheckbox && formData.useWatermark !== undefined) {
        watermarkCheckbox.checked = formData.useWatermark;
      }

      // Clear the saved data after successful restoration
      if (authState.isAuthenticated) {
        sessionStorage.removeItem('generate_form_data');
        console.log('Form data restored and cleared from sessionStorage');
      }
    } catch (error) {
      console.error('Failed to restore form data:', error);
      sessionStorage.removeItem('generate_form_data');
    }
  }

  private setupCreditsCheck(): void {
    if (!authState.isAuthenticated) return;

    const DOCUMENT_COSTS = {
      formal: 34,
      infographic: 52,
      invoice: 28
    };

    const updateCreditsCheck = () => {
      const documentTypeSelect = document.getElementById('document-type-select') as HTMLSelectElement;
      const documentType = documentTypeSelect?.value || 'infographic';
      const cost = DOCUMENT_COSTS[documentType as keyof typeof DOCUMENT_COSTS];
      const userCredits = authState.user?.credits ?? 0;

      // Check if user has enough credits
      const submitBtn = document.getElementById('submit-btn') as HTMLButtonElement;
      const warningDiv = document.getElementById('insufficient-credits-warning');

      if (userCredits < cost) {
        // Insufficient credits - disable button and show warning
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
          submitBtn.title = 'Insufficient credits';
        }
        warningDiv?.classList.remove('hidden');
      } else {
        // Sufficient credits - enable button and hide warning
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
          submitBtn.title = '';
        }
        warningDiv?.classList.add('hidden');
      }
    };

    // Initial check
    updateCreditsCheck();

    // Update when document type changes
    const documentTypeSelect = document.getElementById('document-type-select') as HTMLSelectElement;
    if (documentTypeSelect) {
      documentTypeSelect.addEventListener('change', updateCreditsCheck);
    }

    // Listen for credits updates (after purchase)
    authState.subscribe((isAuthenticated, user) => {
      if (isAuthenticated && user) {
        // Re-check credits
        updateCreditsCheck();
      }
    });
  }

  private setupDescriptionGuide(): void {
    const DESCRIPTION_GUIDES = {
      formal: `
        <strong>Be specific and structured:</strong> Describe the purpose, key topics, and target audience.
        Include section names you want (e.g., "Executive Summary, Market Analysis, Financial Overview").
        Mention the tone (professional, authoritative, persuasive).
        <br><br>
        <strong>Example:</strong> "Create a comprehensive business proposal for a SaaS product launch.
        Include sections on market opportunity, product features, competitive analysis, pricing strategy,
        and implementation timeline. Use a professional, persuasive tone targeting C-level executives."
      `,
      infographic: `
        <strong>Describe your topic, data, and visuals:</strong> Our AI automatically extracts statistics,
        selects optimal chart types (bar, line, pie, gauge), generates relevant images, and structures your document.
        Include specific numbers/percentages for automatic visualization.
        <br><br>
        <strong>Example:</strong> "Create a quarterly business performance report for Q4 2024.
        Include statistics: revenue grew 35% to $2.4M, customer satisfaction at 92%, new users increased by 12,000 (up 28%),
        and market share reached 18%. Show a pie chart of revenue by region (North America 45%, Europe 30%, Asia 25%).
        Generate images of a modern office workspace, team collaboration, and data analytics dashboard.
        Use a professional tone with sections covering financial highlights, customer metrics, growth initiatives, and 2025 outlook.
        Color theme: corporate blue and green."
      `,
      invoice: `
        <strong>Provide complete transaction details:</strong> Include vendor (your business) name and full address,
        customer/client name and address, detailed list of items/services with prices and quantities,
        payment terms, and any special notes.
        <br><br>
        <strong>Example:</strong> "Vendor: Fashion Boutique Ltd, 456 Style Avenue, Los Angeles, CA 90015, USA.
        Customer: Sarah Johnson at Digital Innovations Inc, 789 Tech Plaza, San Francisco, CA 94105.
        Items: Blue Denim Jeans ($45 x 2), White Cotton T-Shirt ($25 x 3), Black Leather Jacket ($120 x 1),
        Red Summer Dress ($60 x 2). Payment terms: Net 30 days. Tax rate: 10%.
        Notes: Thank you for your continued business! Contact us at sales@fashionboutique.com for any questions."
      `
    };

    const updateGuide = () => {
      const documentTypeSelect = document.getElementById('document-type-select') as HTMLSelectElement;
      const guideText = document.getElementById('description-guide-text');

      if (!documentTypeSelect || !guideText) return;

      const documentType = documentTypeSelect.value as keyof typeof DESCRIPTION_GUIDES;
      guideText.innerHTML = DESCRIPTION_GUIDES[documentType] || DESCRIPTION_GUIDES.infographic;
    };

    // Initial update
    updateGuide();

    // Update when document type changes
    const documentTypeSelect = document.getElementById('document-type-select');
    if (documentTypeSelect) {
      documentTypeSelect.addEventListener('change', updateGuide);
    }
  }

  private setupWatermarkToggle(): void {
    let hasLogo = false;

    const updateWatermarkVisibility = () => {
      const watermarkContainer = document.getElementById('watermark-container');
      const documentTypeSelect = document.getElementById('document-type-select') as HTMLSelectElement;
      const watermarkCheckbox = document.getElementById('use-watermark') as HTMLInputElement;

      if (!watermarkContainer || !documentTypeSelect) return;

      const documentType = documentTypeSelect.value;
      const supportsWatermark = documentType === 'formal' || documentType === 'invoice';

      // Show watermark checkbox only if:
      // 1. Document type is formal or invoice
      // 2. Logo has been uploaded
      if (supportsWatermark && hasLogo) {
        watermarkContainer.classList.remove('hidden');
      } else {
        watermarkContainer.classList.add('hidden');
        // Uncheck watermark if hiding
        if (watermarkCheckbox) {
          watermarkCheckbox.checked = false;
        }
      }
    };

    // Listen for logo file selection
    const logoInput = document.getElementById('logo-input') as HTMLInputElement;
    if (logoInput) {
      logoInput.addEventListener('change', (e) => {
        const target = e.target as HTMLInputElement;
        hasLogo = !!(target.files && target.files.length > 0);
        updateWatermarkVisibility();
      });
    }

    // Listen for document type changes
    const documentTypeSelect = document.getElementById('document-type-select');
    if (documentTypeSelect) {
      documentTypeSelect.addEventListener('change', updateWatermarkVisibility);
    }

    // Initial check
    updateWatermarkVisibility();
  }

  private setupLengthVisibility(): void {
    const updateLengthVisibility = () => {
      const lengthContainer = document.getElementById('length-container');
      const lengthInput = document.getElementById('length') as HTMLInputElement;
      const documentTypeSelect = document.getElementById('document-type-select') as HTMLSelectElement;

      if (!lengthContainer || !documentTypeSelect) return;

      const documentType = documentTypeSelect.value;

      // Show length field only for infographic and formal documents
      if (documentType === 'infographic' || documentType === 'formal') {
        lengthContainer.classList.remove('hidden');
        // Re-add required attribute when visible
        if (lengthInput) {
          lengthInput.setAttribute('required', 'required');
        }
      } else {
        lengthContainer.classList.add('hidden');
        // Remove required attribute when hidden
        if (lengthInput) {
          lengthInput.removeAttribute('required');
        }
      }
    };

    // Listen for document type changes
    const documentTypeSelect = document.getElementById('document-type-select');
    if (documentTypeSelect) {
      documentTypeSelect.addEventListener('change', updateLengthVisibility);
    }

    // Initial check
    updateLengthVisibility();
  }

  destroy(): void {
    // Cleanup if needed
    window.removeEventListener('document-generated', this.setupGenerationListener);
  }
}
