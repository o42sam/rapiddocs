/**
 * Mouse Cursor Utility
 * Creates a blinking cursor that follows the mouse position
 */

export class MouseCursor {
  private cursorElement: HTMLDivElement | null = null;
  private mouseX: number = 0;
  private mouseY: number = 0;
  private animationFrameId: number | null = null;

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

    // Add to DOM - it should be behind all content
    document.body.insertBefore(this.cursorElement, document.body.firstChild);

    // Set up mouse tracking
    this.setupMouseTracking();
  }

  /**
   * Set up mouse move event listener
   */
  private setupMouseTracking(): void {
    document.addEventListener('mousemove', (e: MouseEvent) => {
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;

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
      if (this.cursorElement) {
        this.cursorElement.style.opacity = '0';
      }
    });

    // Show cursor when mouse enters window
    document.addEventListener('mouseenter', () => {
      if (this.cursorElement) {
        this.cursorElement.style.opacity = '';
      }
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
   * Destroy the cursor and clean up
   */
  public destroy(): void {
    if (this.cursorElement && this.cursorElement.parentNode) {
      this.cursorElement.parentNode.removeChild(this.cursorElement);
    }

    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  }
}
