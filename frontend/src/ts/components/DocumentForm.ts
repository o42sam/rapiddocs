import { documentApi } from '../api/endpoints';
import { apiClient } from '../api/client';
import { DocumentGenerationRequest, JobStatusResponse } from '../types/document';
import { validateDescription, validateLength, validateFile } from '../utils/validation';
import { ColorPalette } from './ColorPalette';
import { StatisticsForm } from './StatisticsForm';
import { creditsService } from '../services/creditsService';
import { authState } from '../auth/authState';

export class DocumentForm {
  private form: HTMLFormElement;
  private colorPalette: ColorPalette;
  private statisticsForm: StatisticsForm;
  private currentJobId: string | null = null;
  private statusCheckInterval: number | null = null;

  constructor(formId: string) {
    const element = document.getElementById(formId);
    if (!element || !(element instanceof HTMLFormElement)) {
      throw new Error(`Form with id ${formId} not found`);
    }
    this.form = element;

    // Initialize components
    this.colorPalette = new ColorPalette('color-palette-container');
    this.statisticsForm = new StatisticsForm('statistics-form-container');

    this.attachEventListeners();
  }

  private attachEventListeners(): void {
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleSubmit();
    });

    // File input preview
    const logoInput = document.getElementById('logo-input') as HTMLInputElement;
    if (logoInput) {
      logoInput.addEventListener('change', (e) => {
        const target = e.target as HTMLInputElement;
        const file = target.files?.[0];
        this.updateFilePreview(file);
        this.updateWatermarkVisibility();
      });
    }

    // Document type change listener for select element
    const documentTypeSelect = document.getElementById('document-type-select');
    if (documentTypeSelect) {
      documentTypeSelect.addEventListener('change', () => {
        this.updateWatermarkVisibility();
      });
    }
  }

  private updateWatermarkVisibility(): void {
    const watermarkContainer = document.getElementById('watermark-container');
    if (!watermarkContainer) return;

    const documentTypeSelect = document.getElementById('document-type-select') as HTMLSelectElement;
    const documentType = documentTypeSelect?.value || 'infographic';

    const logoInput = document.getElementById('logo-input') as HTMLInputElement;
    const hasLogo = logoInput.files && logoInput.files.length > 0;

    // Show watermark checkbox only if formal or invoice mode is selected AND a logo is uploaded
    if ((documentType === 'formal' || documentType === 'invoice') && hasLogo) {
      watermarkContainer.classList.remove('hidden');
    } else {
      watermarkContainer.classList.add('hidden');
      // Uncheck the watermark checkbox when hiding
      const watermarkCheckbox = document.getElementById('use-watermark') as HTMLInputElement;
      if (watermarkCheckbox) {
        watermarkCheckbox.checked = false;
      }
    }
  }

  private updateFilePreview(file?: File): void {
    const preview = document.getElementById('file-preview');
    if (!preview) return;

    if (file) {
      const error = validateFile(file);
      if (error) {
        preview.innerHTML = `<p class="text-sm text-red-600">${error}</p>`;
      } else {
        preview.innerHTML = `
          <p class="text-sm text-green-600">
            ✓ ${file.name} (${(file.size / 1024).toFixed(1)} KB)
          </p>
        `;
      }
    } else {
      preview.innerHTML = '';
    }
  }

  private async handleSubmit(): Promise<void> {
    // Clear previous errors
    this.clearErrors();

    // Get form values
    const description = (document.getElementById('description') as HTMLTextAreaElement).value;
    const length = parseInt((document.getElementById('length') as HTMLInputElement).value);
    const logoInput = document.getElementById('logo-input') as HTMLInputElement;
    const logo = logoInput.files?.[0];

    // Get document type from select element (not radio buttons)
    const documentTypeSelect = document.getElementById('document-type-select') as HTMLSelectElement;
    const document_type = (documentTypeSelect?.value as 'formal' | 'infographic' | 'invoice') || 'infographic';

    // Get watermark preference
    const watermarkCheckbox = document.getElementById('use-watermark') as HTMLInputElement;
    const use_watermark = watermarkCheckbox?.checked || false;

    // Validate
    const errors: string[] = [];

    const descError = validateDescription(description);
    if (descError) errors.push(descError);

    // Skip length validation for invoices (they don't have word count)
    if (document_type !== 'invoice') {
      const lengthError = validateLength(length);
      if (lengthError) errors.push(lengthError);
    }

    if (logo) {
      const fileError = validateFile(logo);
      if (fileError) errors.push(fileError);
    }

    const statErrors = this.statisticsForm.validate();
    errors.push(...statErrors);

    if (errors.length > 0) {
      this.showErrors(errors);
      return;
    }

    // For invoices, validate the prompt first
    let skipValidation = false;
    if (document_type === 'invoice') {
      const validationResult = await this.validateInvoicePrompt(description);
      if (!validationResult.proceed) {
        return; // User chose not to proceed
      }
      skipValidation = validationResult.skipValidation || false;
    }

    // Build request
    const request: DocumentGenerationRequest & { skip_validation?: boolean } = {
      description,
      length,
      document_type,
      use_watermark,
      statistics: this.statisticsForm.getStatistics(),
      design_spec: this.colorPalette.getSelectedTheme(),
      logo,
      skip_validation: skipValidation,
    };

    // Submit
    try {
      this.showLoading(true);

      // Deduct credits before generating document
      try {
        const deductionResult = await creditsService.deductCredits(document_type);

        // Update user's credits in authState
        const currentUser = authState.user;
        if (currentUser) {
          authState.setAuthenticated({
            ...currentUser,
            credits: deductionResult.new_balance
          });
        }

        console.log(`Credits deducted: ${deductionResult.credits_deducted}, New balance: ${deductionResult.new_balance}`);
      } catch (creditsError: any) {
        // Handle credits deduction error
        const errorMessage = creditsError.response?.data?.detail || 'Failed to deduct credits';
        this.showErrors([errorMessage]);
        this.showLoading(false);
        return;
      }

      // Generate document
      const response = await documentApi.generateDocument(request);

      // Check if validation failed on backend
      if (response.status === 'validation_failed') {
        // Show validation dialog with missing fields
        const dialogResult = await this.showIncompleteDataDialog(response.missing_fields || []);
        if (!dialogResult.proceed) {
          this.showLoading(false);
          return;
        }
        // Retry with skip_validation flag
        request.skip_validation = true;
        const retryResponse = await documentApi.generateDocument(request);
        this.currentJobId = retryResponse.job_id;
        this.startStatusPolling();
      } else {
        this.currentJobId = response.job_id;
        this.startStatusPolling();
      }
    } catch (error: any) {
      this.showErrors([error.response?.data?.detail || 'Failed to start document generation']);
      this.showLoading(false);
    }
  }

  private startStatusPolling(): void {
    if (!this.currentJobId) return;

    this.updateProgress(0, 'Initializing...');

    this.statusCheckInterval = window.setInterval(async () => {
      if (!this.currentJobId) return;

      try {
        const status = await documentApi.getJobStatus(this.currentJobId);
        this.handleStatusUpdate(status);
      } catch (error) {
        console.error('Failed to check status:', error);
      }
    }, 3000); // Check every 3 seconds
  }

  private handleStatusUpdate(status: JobStatusResponse): void {
    this.updateProgress(status.progress, status.current_step);

    if (status.status === 'completed') {
      this.stopStatusPolling();
      this.showSuccess(status.job_id);
    } else if (status.status === 'failed') {
      this.stopStatusPolling();
      this.showErrors([status.error_message || 'Document generation failed']);
      this.showLoading(false);
    }
  }

  private stopStatusPolling(): void {
    if (this.statusCheckInterval) {
      clearInterval(this.statusCheckInterval);
      this.statusCheckInterval = null;
    }
  }

  private updateProgress(progress: number, step: string): void {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    if (progressBar) {
      progressBar.style.width = `${progress}%`;
    }

    if (progressText) {
      progressText.textContent = `${progress}% - ${this.formatStep(step)}`;
    }
  }

  private formatStep(step: string): string {
    const steps: { [key: string]: string } = {
      initializing: 'Initializing...',
      generating_text: 'Generating document text...',
      generating_images: 'Creating AI images...',
      generating_visualizations: 'Creating data visualizations...',
      assembling_pdf: 'Assembling PDF document...',
      completed: 'Completed!',
    };
    return steps[step] || step;
  }

  private showSuccess(jobId: string): void {
    const resultDiv = document.getElementById('result-container');
    if (!resultDiv) return;

    resultDiv.innerHTML = `
      <div class="bg-green-50 border border-green-200 rounded-lg p-6">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-lg font-semibold text-green-800">Document Generated Successfully!</h3>
        </div>
        <button
          id="download-btn"
          class="px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition"
        >
          Download PDF
        </button>
      </div>
    `;

    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
      downloadBtn.addEventListener('click', () => this.downloadPDF(jobId));
    }

    this.showLoading(false);
  }

  private async downloadPDF(jobId: string): Promise<void> {
    try {
      const blob = await documentApi.downloadDocument(jobId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document-${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error: any) {
      this.showErrors([error.response?.data?.detail || 'Failed to download PDF']);
    }
  }

  private showLoading(show: boolean): void {
    const loadingDiv = document.getElementById('loading-container');
    const submitBtn = document.getElementById('submit-btn') as HTMLButtonElement;

    if (loadingDiv) {
      loadingDiv.classList.toggle('hidden', !show);
    }

    if (submitBtn) {
      submitBtn.disabled = show;
      submitBtn.textContent = show ? 'Generating...' : 'Generate Document';
    }
  }

  private showErrors(errors: string[]): void {
    const errorDiv = document.getElementById('error-container');
    if (!errorDiv) return;

    errorDiv.innerHTML = `
      <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-red-800 mb-2">Please fix the following errors:</h4>
        <ul class="list-disc list-inside space-y-1">
          ${errors.map((error) => `<li class="text-sm text-red-600">${error}</li>`).join('')}
        </ul>
      </div>
    `;

    errorDiv.classList.remove('hidden');
  }

  private clearErrors(): void {
    const errorDiv = document.getElementById('error-container');
    if (errorDiv) {
      errorDiv.classList.add('hidden');
      errorDiv.innerHTML = '';
    }

    const resultDiv = document.getElementById('result-container');
    if (resultDiv) {
      resultDiv.innerHTML = '';
    }
  }

  private async validateInvoicePrompt(description: string): Promise<{ proceed: boolean, skipValidation?: boolean }> {
    try {
      // Create form data for validation
      const formData = new FormData();
      formData.append('description', description);

      const response = await apiClient.post('/validate/invoice', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const result = response.data;

      if (!result.is_complete) {
        // Show dialog with missing fields
        return await this.showIncompleteDataDialog(result.missing_fields);
      }

      return { proceed: true };
    } catch (error) {
      console.error('Validation failed:', error);
      // If validation fails, let user proceed anyway
      return { proceed: true };
    }
  }

  private showIncompleteDataDialog(missingFields: string[]): Promise<{ proceed: boolean, skipValidation?: boolean }> {
    return new Promise((resolve) => {
      // Add halo effect to description field
      const descriptionField = document.getElementById('description');
      if (descriptionField) {
        descriptionField.classList.add('halo-effect');
      }

      // Create dialog overlay
      const overlay = document.createElement('div');
      overlay.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center';
      overlay.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div class="flex items-start mb-4">
            <svg class="w-6 h-6 text-yellow-500 mr-2 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Incomplete Invoice Information</h3>
              <p class="text-sm text-gray-600 mb-3">The following information is missing or using placeholders:</p>
              <ul class="list-disc list-inside text-sm text-gray-700 space-y-1 mb-4">
                ${missingFields.map(field => `<li>${field}</li>`).join('')}
              </ul>
              <p class="text-sm text-gray-600">Would you like to continue anyway or update your description?</p>
            </div>
          </div>
          <div class="flex justify-end space-x-3">
            <button id="dialog-cancel" class="px-4 py-2 text-gray-600 hover:text-gray-800 transition">
              Update Description
            </button>
            <button id="dialog-proceed" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
              Continue Anyway
            </button>
          </div>
        </div>
      `;

      document.body.appendChild(overlay);

      // Handle dialog buttons
      const cancelBtn = document.getElementById('dialog-cancel');
      const proceedBtn = document.getElementById('dialog-proceed');

      if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
          document.body.removeChild(overlay);
          // Keep halo effect and focus the description field
          if (descriptionField) {
            (descriptionField as HTMLTextAreaElement).focus();
            // Remove halo after a delay
            setTimeout(() => {
              descriptionField.classList.remove('halo-effect');
            }, 3000);
          }
          resolve({ proceed: false });
        });
      }

      if (proceedBtn) {
        proceedBtn.addEventListener('click', () => {
          document.body.removeChild(overlay);
          // Remove halo effect
          if (descriptionField) {
            descriptionField.classList.remove('halo-effect');
          }
          resolve({ proceed: true, skipValidation: true });
        });
      }
    });
  }
}
