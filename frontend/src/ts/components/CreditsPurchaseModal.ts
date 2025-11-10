import { creditsService, CreditsPackage } from '../services/creditsService';
import { bitcoinService, BitcoinPaymentStatusResponse } from '../services/bitcoinService';
import { authState } from '../auth/authState';

export class CreditsPurchaseModal {
  private modal: HTMLElement | null = null;
  private packages: CreditsPackage[] = [];
  private currentPaymentId: string | null = null;
  private statusCheckInterval: number | null = null;
  private countdownInterval: number | null = null;
  private expiresAt: Date | null = null;

  constructor() {
    this.init();
  }

  private async init(): Promise<void> {
    // Listen for open modal event
    window.addEventListener('open-credits-modal', () => {
      this.open();
    });

    // Fetch packages
    try {
      this.packages = await creditsService.getPackages();
    } catch (error) {
      console.error('Failed to fetch credits packages:', error);
    }
  }

  private createModal(): HTMLElement {
    const modal = document.createElement('div');
    modal.id = 'credits-purchase-modal';
    modal.className = 'hidden fixed inset-0 bg-gray-900 bg-opacity-50 overflow-y-auto h-full w-full z-50 backdrop-blur-sm';

    modal.innerHTML = `
      <div class="relative top-0 sm:top-10 mx-auto p-2 sm:p-5 w-full sm:max-w-4xl min-h-screen sm:min-h-0 sm:mb-10">
        <div class="bg-white rounded-none sm:rounded-2xl shadow-2xl overflow-hidden min-h-screen sm:min-h-0">
          <!-- Header -->
          <div class="bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-4 sm:px-6 sm:py-6 md:px-8 md:py-8">
            <div class="flex justify-between items-start sm:items-center gap-2">
              <div class="flex-1">
                <h2 class="text-xl sm:text-2xl md:text-3xl font-bold text-white">Buy Credits</h2>
                <p class="text-blue-100 mt-1 text-sm sm:text-base">Pay with Bitcoin to continue creating documents</p>
              </div>
              <button id="close-credits-modal" class="text-white hover:text-gray-200 transition-colors flex-shrink-0 p-1">
                <svg class="w-6 h-6 sm:w-7 sm:h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Body -->
          <div class="px-3 py-4 sm:px-6 sm:py-8 md:px-8">
            <!-- Packages Grid -->
            <div id="packages-section">
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
                ${this.renderPackages()}
              </div>
            </div>

            <!-- Bitcoin Payment Section -->
            <div id="bitcoin-payment-section" class="hidden">
              <div class="border-t border-gray-200 pt-4 sm:pt-6">
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4 sm:mb-6">
                  <h3 class="text-lg sm:text-xl font-bold text-gray-900">Bitcoin Payment</h3>
                  <button id="back-to-packages-btn" class="text-blue-600 hover:text-blue-700 text-sm font-medium text-left sm:text-right">
                    ← Back to Packages
                  </button>
                </div>

                <!-- Loading State -->
                <div id="payment-loading" class="text-center py-6 sm:py-8">
                  <div class="inline-block animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 border-b-2 border-blue-600"></div>
                  <p class="mt-4 text-gray-600 text-sm sm:text-base">Generating payment address...</p>
                </div>

                <!-- Payment Details -->
                <div id="payment-details" class="hidden">
                  <div class="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4 sm:p-6 mb-4 sm:mb-6">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                      <!-- Payment Info -->
                      <div class="order-2 lg:order-1">
                        <div class="mb-3 sm:mb-4">
                          <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">Package:</label>
                          <p id="payment-package-info" class="text-base sm:text-lg font-semibold text-gray-900"></p>
                        </div>

                        <div class="mb-3 sm:mb-4">
                          <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">Amount to Pay:</label>
                          <div class="flex flex-wrap items-baseline gap-2">
                            <p id="payment-btc-amount" class="text-xl sm:text-2xl font-bold text-orange-600 break-all"></p>
                            <p id="payment-usd-amount" class="text-xs sm:text-sm text-gray-600"></p>
                          </div>
                        </div>

                        <div class="mb-3 sm:mb-4">
                          <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">Bitcoin Address:</label>
                          <div class="flex flex-col sm:flex-row gap-2">
                            <input
                              type="text"
                              id="payment-address"
                              readonly
                              class="flex-1 w-full px-2 sm:px-3 py-2 bg-white border border-gray-300 rounded-lg text-xs sm:text-sm font-mono break-all"
                            />
                            <button
                              id="copy-address-btn"
                              class="w-full sm:w-auto px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                            >
                              Copy
                            </button>
                          </div>
                        </div>

                        <!-- Countdown Timer -->
                        <div class="mb-3 sm:mb-4">
                          <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">Time Remaining:</label>
                          <div id="payment-countdown" class="flex items-center justify-center gap-2 bg-gradient-to-r from-orange-100 to-red-100 border-2 border-orange-300 rounded-lg p-2 sm:p-3">
                            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span id="countdown-timer" class="text-xl sm:text-2xl font-bold text-orange-700 font-mono">59:59</span>
                          </div>
                        </div>

                        <div class="bg-yellow-50 border border-yellow-200 rounded-md p-3 sm:p-4 text-xs sm:text-sm text-yellow-800">
                          <strong>⚠️ Important:</strong> Send exactly the amount shown above to the Bitcoin address before the timer expires.
                        </div>
                      </div>

                      <!-- QR Code -->
                      <div class="flex flex-col items-center justify-center order-1 lg:order-2">
                        <p class="text-xs sm:text-sm font-medium text-gray-700 mb-2 sm:mb-3">Scan QR Code:</p>
                        <div class="bg-white p-3 sm:p-4 rounded-lg border-2 border-gray-200">
                          <img id="payment-qr-code" src="" alt="Bitcoin QR Code" class="w-40 h-40 sm:w-48 sm:h-48" />
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Payment Status -->
                  <div id="payment-status" class="bg-white border-2 border-gray-200 rounded-lg p-4 sm:p-6">
                    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                      <h4 class="text-base sm:text-lg font-semibold text-gray-900">Payment Status</h4>
                      <span id="status-badge" class="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs sm:text-sm font-medium rounded-full self-start sm:self-auto">
                        Waiting for payment
                      </span>
                    </div>

                    <div id="status-message" class="text-gray-600 mb-4 text-sm sm:text-base">
                      Waiting for Bitcoin transaction...
                    </div>

                    <!-- Progress Bar (for confirmations) -->
                    <div id="confirmation-progress" class="hidden">
                      <div class="flex justify-between text-xs sm:text-sm text-gray-600 mb-2">
                        <span>Confirmations:</span>
                        <span id="confirmations-text">0 / 3</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2 sm:h-3">
                        <div id="confirmations-bar" class="bg-blue-600 h-2 sm:h-3 rounded-full transition-all duration-500" style="width: 0%"></div>
                      </div>
                    </div>

                    <!-- Transaction Hash -->
                    <div id="tx-hash-section" class="hidden mt-4 text-xs sm:text-sm">
                      <span class="text-gray-600">Transaction: </span>
                      <a id="tx-hash-link" href="#" target="_blank" class="text-blue-600 hover:underline font-mono break-all"></a>
                    </div>
                  </div>
                </div>

                <!-- Error Message -->
                <div id="payment-error" class="hidden bg-red-50 border border-red-200 text-red-700 px-3 py-2 sm:px-4 sm:py-3 rounded-lg text-xs sm:text-sm mt-4"></div>
              </div>
            </div>

            <!-- Success Section -->
            <div id="success-section" class="hidden">
              <div class="text-center py-6 sm:py-8 px-4">
                <div class="mx-auto flex items-center justify-center h-12 w-12 sm:h-16 sm:w-16 rounded-full bg-green-100 mb-4">
                  <svg class="h-8 w-8 sm:h-10 sm:w-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 class="text-xl sm:text-2xl font-bold text-gray-900 mb-2">Credits Purchased!</h3>
                <p class="text-sm sm:text-base text-gray-600 mb-4" id="success-message"></p>
                <button
                  id="close-success-btn"
                  class="btn-primary w-full sm:w-auto"
                >
                  Start Creating
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    return modal;
  }

  private renderPackages(): string {
    if (this.packages.length === 0) {
      return `
        <div class="col-span-3 text-center text-gray-500 py-8">
          Loading packages...
        </div>
      `;
    }

    const packageIcons = {
      small: `<svg class="w-16 h-16 mx-auto mb-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 000 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
      </svg>`,
      medium: `<svg class="w-16 h-16 mx-auto mb-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clip-rule="evenodd" />
      </svg>`,
      large: `<svg class="w-16 h-16 mx-auto mb-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
      </svg>`
    };

    return this.packages.map((pkg) => `
      <div class="package-card relative border-2 border-gray-200 rounded-xl p-4 sm:p-6 hover:border-blue-500 hover:shadow-lg transition-all cursor-pointer ${pkg.id === 'medium' ? 'border-blue-500 shadow-lg' : ''}" data-package-id="${pkg.id}">
        ${pkg.id === 'medium' ? '<div class="absolute top-0 right-0 bg-blue-500 text-white text-xs font-bold px-2 sm:px-3 py-1 rounded-bl-lg rounded-tr-lg">POPULAR</div>' : ''}

        <div class="hidden sm:block">${packageIcons[pkg.id as keyof typeof packageIcons] || ''}</div>

        <h3 class="text-lg sm:text-xl font-bold text-gray-900 text-center mb-2">${pkg.name}</h3>

        <div class="text-center mb-3 sm:mb-4">
          <div class="flex items-center justify-center mb-2">
            <svg class="w-6 h-6 sm:w-8 sm:h-8 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd" />
            </svg>
          </div>
          <p class="text-2xl sm:text-3xl font-bold text-gray-900">${pkg.credits.toLocaleString()}</p>
          <p class="text-xs sm:text-sm text-gray-500">Credits</p>
        </div>

        <div class="text-center mb-3 sm:mb-4">
          <p class="text-xl sm:text-2xl font-bold text-blue-600">$${pkg.price.toFixed(2)}</p>
          <p class="text-xs text-gray-500 mt-1">${(pkg.price / pkg.credits * 1000).toFixed(2)}¢ per 1000 credits</p>
        </div>

        <button class="w-full btn-primary select-package-btn text-sm sm:text-base py-2 sm:py-2.5" data-package-id="${pkg.id}">
          Pay with Bitcoin
        </button>
      </div>
    `).join('');
  }

  private attachEventListeners(): void {
    if (!this.modal) return;

    // Close modal
    const closeBtn = this.modal.querySelector('#close-credits-modal');
    const closeSuccessBtn = this.modal.querySelector('#close-success-btn');

    [closeBtn, closeSuccessBtn].forEach(btn => {
      btn?.addEventListener('click', () => this.close());
    });

    // Close on outside click
    this.modal.addEventListener('click', (e) => {
      if (e.target === this.modal) {
        this.close();
      }
    });

    // Package selection
    this.modal.querySelectorAll('.select-package-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const packageId = (e.target as HTMLElement).getAttribute('data-package-id');
        if (packageId) {
          this.selectPackage(packageId);
        }
      });
    });

    // Package card click
    this.modal.querySelectorAll('.package-card').forEach(card => {
      card.addEventListener('click', () => {
        const packageId = card.getAttribute('data-package-id');
        if (packageId) {
          this.selectPackage(packageId);
        }
      });
    });

    // Back to packages
    const backBtn = this.modal.querySelector('#back-to-packages-btn');
    backBtn?.addEventListener('click', () => {
      this.stopStatusPolling();
      this.stopCountdown();
      this.showPackagesSection();
    });

    // Copy address button
    const copyBtn = this.modal.querySelector('#copy-address-btn');
    copyBtn?.addEventListener('click', () => this.copyAddress());
  }

  private async selectPackage(packageId: string): Promise<void> {
    const pkg = this.packages.find(p => p.id === packageId);
    if (!pkg || !this.modal) return;

    // Show payment section and hide packages
    this.showPaymentSection();

    try {
      // Initiate Bitcoin payment
      const response = await bitcoinService.initiateBitcoinPayment({
        package: packageId as 'small' | 'medium' | 'large'
      });

      this.currentPaymentId = response.payment_id;
      this.expiresAt = new Date(response.expires_at);

      // Update UI with payment details
      const packageInfo = this.modal.querySelector('#payment-package-info');
      const btcAmount = this.modal.querySelector('#payment-btc-amount');
      const usdAmount = this.modal.querySelector('#payment-usd-amount');
      const address = this.modal.querySelector('#payment-address') as HTMLInputElement;
      const qrCode = this.modal.querySelector('#payment-qr-code') as HTMLImageElement;

      if (packageInfo) packageInfo.textContent = `${pkg.name} - ${pkg.credits.toLocaleString()} Credits`;
      if (btcAmount) btcAmount.textContent = `${response.amount_btc.toFixed(8)} BTC`;
      if (usdAmount) usdAmount.textContent = `($${response.amount_usd.toFixed(2)} USD)`;
      if (address) address.value = response.payment_address;
      if (qrCode) qrCode.src = `data:image/png;base64,${response.qr_code_data}`;

      // Hide loading, show details
      this.modal.querySelector('#payment-loading')?.classList.add('hidden');
      this.modal.querySelector('#payment-details')?.classList.remove('hidden');

      // Start countdown timer
      this.startCountdown();

      // Start polling for payment status
      this.startStatusPolling();

    } catch (error: any) {
      const errorDiv = this.modal.querySelector('#payment-error');
      if (errorDiv) {
        errorDiv.textContent = error.response?.data?.detail || 'Failed to initiate payment. Please try again.';
        errorDiv.classList.remove('hidden');
      }
      this.modal.querySelector('#payment-loading')?.classList.add('hidden');
    }
  }

  private startStatusPolling(): void {
    if (!this.currentPaymentId) return;

    this.statusCheckInterval = window.setInterval(async () => {
      await this.checkPaymentStatus();
    }, 5000); // Check every 5 seconds
  }

  private stopStatusPolling(): void {
    if (this.statusCheckInterval) {
      clearInterval(this.statusCheckInterval);
      this.statusCheckInterval = null;
    }
  }

  private startCountdown(): void {
    if (!this.expiresAt) return;

    this.updateCountdown(); // Initial update

    this.countdownInterval = window.setInterval(() => {
      this.updateCountdown();
    }, 1000); // Update every second
  }

  private stopCountdown(): void {
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval);
      this.countdownInterval = null;
    }
  }

  private updateCountdown(): void {
    if (!this.modal || !this.expiresAt) return;

    const countdownElement = this.modal.querySelector('#countdown-timer');
    const countdownContainer = this.modal.querySelector('#payment-countdown');
    if (!countdownElement || !countdownContainer) return;

    const now = new Date().getTime();
    const expiry = this.expiresAt.getTime();
    const timeLeft = expiry - now;

    if (timeLeft <= 0) {
      // Payment expired
      countdownElement.textContent = '00:00';
      countdownContainer.className = 'flex items-center justify-center gap-2 bg-red-100 border-2 border-red-400 rounded-lg p-3';

      const timerText = countdownElement as HTMLElement;
      timerText.className = 'text-2xl font-bold text-red-700 font-mono';

      this.stopCountdown();
      this.stopStatusPolling();

      // Show expired message
      const statusMessage = this.modal.querySelector('#status-message');
      if (statusMessage) {
        statusMessage.textContent = 'Payment expired. Please create a new payment.';
      }

      const statusBadge = this.modal.querySelector('#status-badge');
      if (statusBadge) {
        statusBadge.className = 'px-3 py-1 text-sm font-medium rounded-full bg-red-100 text-red-800';
        statusBadge.textContent = 'Expired';
      }

      return;
    }

    // Calculate time components
    const hours = Math.floor(timeLeft / (1000 * 60 * 60));
    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

    // Format time string
    let timeString = '';
    if (hours > 0) {
      timeString = `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    } else {
      timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    countdownElement.textContent = timeString;

    // Change color based on time remaining
    const timerText = countdownElement as HTMLElement;
    if (timeLeft < 5 * 60 * 1000) { // Less than 5 minutes
      countdownContainer.className = 'flex items-center justify-center gap-2 bg-gradient-to-r from-red-100 to-red-200 border-2 border-red-400 rounded-lg p-3';
      timerText.className = 'text-2xl font-bold text-red-700 font-mono animate-pulse';
    } else if (timeLeft < 15 * 60 * 1000) { // Less than 15 minutes
      countdownContainer.className = 'flex items-center justify-center gap-2 bg-gradient-to-r from-yellow-100 to-orange-100 border-2 border-yellow-400 rounded-lg p-3';
      timerText.className = 'text-2xl font-bold text-orange-700 font-mono';
    } else {
      countdownContainer.className = 'flex items-center justify-center gap-2 bg-gradient-to-r from-orange-100 to-red-100 border-2 border-orange-300 rounded-lg p-3';
      timerText.className = 'text-2xl font-bold text-orange-700 font-mono';
    }
  }

  private async checkPaymentStatus(): Promise<void> {
    if (!this.currentPaymentId || !this.modal) return;

    try {
      const status = await bitcoinService.checkPaymentStatus({
        payment_id: this.currentPaymentId
      });

      this.updatePaymentStatus(status);

      // If confirmed, process the payment
      // Note: Background processor also handles this automatically,
      // but we call it here for immediate user feedback
      if (status.status === 'confirmed' && status.confirmations >= status.required_confirmations) {
        this.stopStatusPolling();
        this.stopCountdown();
        await this.processPayment(status.payment_id);
      }

      // If payment was already processed by background processor, show success
      if (status.status === 'forwarded') {
        this.stopStatusPolling();
        this.stopCountdown();

        // Update user credits in authState
        const currentUser = authState.user;
        if (currentUser) {
          authState.setAuthenticated({
            ...currentUser,
            credits: currentUser.credits + status.credits
          });
        }

        // Show success
        this.showSuccessSection(status.credits, (currentUser?.credits || 0) + status.credits);
      }

      // If expired or failed, stop polling
      if (status.status === 'expired' || status.status === 'failed') {
        this.stopStatusPolling();
        this.stopCountdown();
      }

    } catch (error) {
      console.error('Failed to check payment status:', error);
    }
  }

  private updatePaymentStatus(status: BitcoinPaymentStatusResponse): void {
    if (!this.modal) return;

    const statusBadge = this.modal.querySelector('#status-badge');
    const statusMessage = this.modal.querySelector('#status-message');
    const confirmationProgress = this.modal.querySelector('#confirmation-progress');
    const confirmationsText = this.modal.querySelector('#confirmations-text');
    const confirmationsBar = this.modal.querySelector('#confirmations-bar') as HTMLElement;
    const txHashSection = this.modal.querySelector('#tx-hash-section');
    const txHashLink = this.modal.querySelector('#tx-hash-link') as HTMLAnchorElement;

    // Update status badge
    const statusColors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirming: 'bg-blue-100 text-blue-800',
      confirmed: 'bg-green-100 text-green-800',
      forwarded: 'bg-green-100 text-green-800',
      expired: 'bg-red-100 text-red-800',
      failed: 'bg-red-100 text-red-800'
    };

    if (statusBadge) {
      statusBadge.className = `px-3 py-1 text-sm font-medium rounded-full ${statusColors[status.status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'}`;
      statusBadge.textContent = status.status.charAt(0).toUpperCase() + status.status.slice(1);
    }

    // Update status message
    if (statusMessage) {
      statusMessage.textContent = status.message;
    }

    // Update confirmation progress
    if (status.confirmations > 0) {
      confirmationProgress?.classList.remove('hidden');
      if (confirmationsText) {
        confirmationsText.textContent = `${status.confirmations} / ${status.required_confirmations}`;
      }
      if (confirmationsBar) {
        const progress = (status.confirmations / status.required_confirmations) * 100;
        confirmationsBar.style.width = `${Math.min(progress, 100)}%`;
      }
    }

    // Show transaction hash
    if (status.tx_hash && txHashSection && txHashLink) {
      txHashSection.classList.remove('hidden');
      txHashLink.textContent = status.tx_hash.substring(0, 16) + '...';
      txHashLink.href = `https://blockstream.info/testnet/tx/${status.tx_hash}`;
    }
  }

  private async processPayment(paymentId: string): Promise<void> {
    if (!this.modal) return;

    try {
      const response = await bitcoinService.confirmPayment(paymentId);

      // Update user credits in authState
      const currentUser = authState.user;
      if (currentUser) {
        authState.setAuthenticated({
          ...currentUser,
          credits: response.new_balance
        });
      }

      // Show success
      this.showSuccessSection(response.credits_added, response.new_balance);

    } catch (error: any) {
      const errorDiv = this.modal.querySelector('#payment-error');
      if (errorDiv) {
        errorDiv.textContent = error.response?.data?.detail || 'Failed to process payment. Please contact support.';
        errorDiv.classList.remove('hidden');
      }
    }
  }

  private showPackagesSection(): void {
    if (!this.modal) return;
    this.modal.querySelector('#packages-section')?.classList.remove('hidden');
    this.modal.querySelector('#bitcoin-payment-section')?.classList.add('hidden');
    this.modal.querySelector('#success-section')?.classList.add('hidden');
  }

  private showPaymentSection(): void {
    if (!this.modal) return;
    this.modal.querySelector('#packages-section')?.classList.add('hidden');
    this.modal.querySelector('#bitcoin-payment-section')?.classList.remove('hidden');
    this.modal.querySelector('#success-section')?.classList.add('hidden');
    this.modal.querySelector('#payment-loading')?.classList.remove('hidden');
    this.modal.querySelector('#payment-details')?.classList.add('hidden');
  }

  private showSuccessSection(creditsAdded: number, newBalance: number): void {
    if (!this.modal) return;

    const successMessage = this.modal.querySelector('#success-message');
    if (successMessage) {
      successMessage.textContent = `Successfully added ${creditsAdded} credits to your account. Your new balance is ${newBalance} credits.`;
    }

    this.modal.querySelector('#packages-section')?.classList.add('hidden');
    this.modal.querySelector('#bitcoin-payment-section')?.classList.add('hidden');
    this.modal.querySelector('#success-section')?.classList.remove('hidden');
  }

  private copyAddress(): void {
    if (!this.modal) return;

    const addressInput = this.modal.querySelector('#payment-address') as HTMLInputElement;
    const copyBtn = this.modal.querySelector('#copy-address-btn');

    if (addressInput && copyBtn) {
      addressInput.select();
      document.execCommand('copy');

      const originalText = copyBtn.textContent;
      copyBtn.textContent = 'Copied!';
      copyBtn.classList.add('bg-green-600');
      copyBtn.classList.remove('bg-blue-600');

      setTimeout(() => {
        copyBtn.textContent = originalText;
        copyBtn.classList.remove('bg-green-600');
        copyBtn.classList.add('bg-blue-600');
      }, 2000);
    }
  }

  open(): void {
    if (!this.modal) {
      this.modal = this.createModal();
      document.body.appendChild(this.modal);
      this.attachEventListeners();
    }

    this.modal.classList.remove('hidden');
    this.showPackagesSection();
    this.currentPaymentId = null;
    this.expiresAt = null;
    this.stopStatusPolling();
    this.stopCountdown();
  }

  close(): void {
    if (this.modal) {
      this.modal.classList.add('hidden');
      this.stopStatusPolling();
      this.stopCountdown();
    }
  }
}
