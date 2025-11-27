/**
 * Loading Screen Component
 * Displays a loading screen with progress bar and pulsating logo during page transitions
 */

export class LoadingScreen {
  private element: HTMLDivElement;
  private progressBar: HTMLDivElement;
  private progress: number = 0;
  private intervalId: number | null = null;

  constructor() {
    this.element = this.createElement();
    this.progressBar = this.element.querySelector('#loading-progress-bar') as HTMLDivElement;
  }

  private createElement(): HTMLDivElement {
    const container = document.createElement('div');
    container.id = 'loading-screen';
    container.className = 'fixed inset-0 z-50 bg-white flex flex-col items-center justify-center';
    container.style.display = 'none';

    container.innerHTML = `
      <!-- Progress Bar Container (thin bar at the top) -->
      <div class="absolute top-0 left-0 right-0 h-1 bg-gray-200 overflow-hidden">
        <div id="loading-progress-bar" class="h-full bg-gradient-to-r from-primary-600 via-primary-500 to-primary-600 transition-all duration-300 ease-out" style="width: 0%"></div>
      </div>

      <!-- Pulsating Logo Container -->
      <div class="flex flex-col items-center justify-center">
        <!-- RapidDocs Logo with Pulsating Animation -->
        <div class="pulsating-logo mb-6">
          <img src="/rd-logo.svg" alt="RapidDocs Logo" class="w-32 h-32 object-contain" />
        </div>

        <!-- Loading Text -->
        <div class="text-center">
          <p class="text-xl font-semibold text-gray-700 mb-2">Loading...</p>
          <p class="text-sm text-gray-500">Please wait while we prepare your page</p>
        </div>
      </div>
    `;

    return container;
  }

  /**
   * Show the loading screen and start progress animation
   */
  public show(): void {
    // Reset progress
    this.progress = 0;
    this.updateProgressBar();

    // Show the loading screen
    this.element.style.display = 'flex';

    // Simulate progress
    this.startProgressAnimation();
  }

  /**
   * Hide the loading screen
   */
  public hide(): void {
    // Complete the progress bar
    this.progress = 100;
    this.updateProgressBar();

    // Stop animation
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    // Fade out and hide after a short delay
    setTimeout(() => {
      this.element.style.opacity = '0';
      this.element.style.transition = 'opacity 0.3s ease-out';

      setTimeout(() => {
        this.element.style.display = 'none';
        this.element.style.opacity = '1';
        this.element.style.transition = '';
      }, 300);
    }, 200);
  }

  /**
   * Update the progress bar width
   */
  private updateProgressBar(): void {
    this.progressBar.style.width = `${this.progress}%`;
  }

  /**
   * Simulate progress animation
   * Progress moves faster at the beginning and slows down near completion
   */
  private startProgressAnimation(): void {
    // Clear any existing interval
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
    }

    // Animate progress
    this.intervalId = window.setInterval(() => {
      if (this.progress < 90) {
        // Increment progress based on current value (slower as it approaches 90%)
        const increment = Math.max(0.5, (90 - this.progress) / 20);
        this.progress = Math.min(90, this.progress + increment);
        this.updateProgressBar();
      }
    }, 50);
  }

  /**
   * Set progress manually (useful for actual loading progress)
   * @param value Progress percentage (0-100)
   */
  public setProgress(value: number): void {
    this.progress = Math.min(100, Math.max(0, value));
    this.updateProgressBar();
  }

  /**
   * Get the loading screen element
   */
  public getElement(): HTMLDivElement {
    return this.element;
  }

  /**
   * Mount the loading screen to the DOM
   */
  public mount(parent: HTMLElement = document.body): void {
    parent.appendChild(this.element);
  }

  /**
   * Unmount the loading screen from the DOM
   */
  public unmount(): void {
    if (this.element.parentElement) {
      this.element.parentElement.removeChild(this.element);
    }
  }
}

// Export singleton instance
export const loadingScreen = new LoadingScreen();
