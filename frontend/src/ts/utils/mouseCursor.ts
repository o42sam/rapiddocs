/**
 * Mouse Cursor Utility
 * Creates a blinking cursor that follows the mouse position
 * Only shows after 15 seconds of mouse inactivity
 */

export class MouseCursor {
  private cursorElement: HTMLDivElement | null = null;
  private mouseX: number = 0;
  private mouseY: number = 0;
  private animationFrameId: number | null = null;
  private inactivityTimer: number | null = null;
  private isVisible: boolean = false;
  private readonly INACTIVITY_DELAY: number = 15000; // 15 seconds

  constructor() {
    this.init();
  }

  /**
   * Initialize the cursor element and event listeners
   */
  private init(): void {
    // Create cursor element
    this.cursorElement = document.createElement('div');
    this.cursorElement.id = 'mouse-cursor';
    this.cursorElement.style.left = '0px';
    this.cursorElement.style.top = '0px';
    this.cursorElement.style.opacity = '0'; // Initially hidden
    this.cursorElement.style.transition = 'opacity 0.3s ease';

    // Add to DOM - it should be behind all content
    document.body.insertBefore(this.cursorElement, document.body.firstChild);

    // Set up mouse tracking
    this.setupMouseTracking();

    // Start the inactivity timer
    this.startInactivityTimer();
  }

  /**
   * Set up mouse move event listener
   */
  private setupMouseTracking(): void {
    document.addEventListener('mousemove', (e: MouseEvent) => {
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;

      // Hide cursor on mouse movement
      this.hideCursor();

      // Restart inactivity timer
      this.startInactivityTimer();

      // Use requestAnimationFrame for smooth updates
      if (!this.animationFrameId) {
        this.animationFrameId = requestAnimationFrame(() => {
          this.updateCursorPosition();
          this.animationFrameId = null;
        });
      }
    });

    // Hide cursor when mouse leaves window
    document.addEventListener('mouseleave', () => {
      this.hideCursor();
      this.clearInactivityTimer();
    });

    // Restart timer when mouse enters window
    document.addEventListener('mouseenter', () => {
      this.startInactivityTimer();
    });

    // Also hide on any mouse button click
    document.addEventListener('click', () => {
      this.hideCursor();
      this.startInactivityTimer();
    });

    // Hide on scroll
    document.addEventListener('scroll', () => {
      this.hideCursor();
      this.startInactivityTimer();
    });
  }

  /**
   * Update the cursor's position
   */
  private updateCursorPosition(): void {
    if (this.cursorElement) {
      this.cursorElement.style.left = `${this.mouseX}px`;
      this.cursorElement.style.top = `${this.mouseY}px`;
    }
  }

  /**
   * Start or restart the inactivity timer
   */
  private startInactivityTimer(): void {
    // Clear existing timer
    this.clearInactivityTimer();

    // Start new timer
    this.inactivityTimer = window.setTimeout(() => {
      this.showCursor();
    }, this.INACTIVITY_DELAY);
  }

  /**
   * Clear the inactivity timer
   */
  private clearInactivityTimer(): void {
    if (this.inactivityTimer !== null) {
      clearTimeout(this.inactivityTimer);
      this.inactivityTimer = null;
    }
  }

  /**
   * Show the cursor
   */
  private showCursor(): void {
    if (this.cursorElement && !this.isVisible) {
      this.cursorElement.style.opacity = '1';
      this.isVisible = true;
    }
  }

  /**
   * Hide the cursor
   */
  private hideCursor(): void {
    if (this.cursorElement && this.isVisible) {
      this.cursorElement.style.opacity = '0';
      this.isVisible = false;
    }
  }

  /**
   * Destroy the cursor and clean up
   */
  public destroy(): void {
    // Clear timer
    this.clearInactivityTimer();

    // Remove element
    if (this.cursorElement && this.cursorElement.parentNode) {
      this.cursorElement.parentNode.removeChild(this.cursorElement);
    }

    // Cancel animation frame
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  }
}
