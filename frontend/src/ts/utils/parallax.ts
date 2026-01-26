/**
 * Parallax Scrolling Utility
 * Provides smooth parallax scrolling effects for different elements
 */

interface ParallaxElement {
  element: HTMLElement;
  speed: number;
  offset: number;
}

export class ParallaxController {
  private parallaxElements: ParallaxElement[] = [];
  private rafId: number | null = null;
  private lastScrollY: number = 0;
  private ticking: boolean = false;

  constructor() {
    this.handleScroll = this.handleScroll.bind(this);
    this.updateElements = this.updateElements.bind(this);
  }

  /**
   * Register an element for parallax scrolling
   * @param element - The HTML element to apply parallax to
   * @param speed - Speed factor:
   *   - Positive values (0.1 to 1): Element moves opposite to scroll (true parallax)
   *   - Negative values (-1 to -0.1): Element moves with scroll (background effect)
   *   - Smaller absolute values = less movement
   * @param offset - Initial offset in pixels
   */
  public registerElement(element: HTMLElement, speed: number = 0.5, offset: number = 0): void {
    if (!element) return;

    this.parallaxElements.push({
      element,
      speed,
      offset
    });

    // Set initial transform
    this.applyTransform(element, offset);
  }

  /**
   * Register multiple elements with the same settings
   */
  public registerElements(selector: string, speed: number = 0.5, offset: number = 0): void {
    const elements = document.querySelectorAll<HTMLElement>(selector);
    elements.forEach(element => {
      this.registerElement(element, speed, offset);
    });
  }

  /**
   * Start listening for scroll events
   */
  public start(): void {
    window.addEventListener('scroll', this.handleScroll, { passive: true });
    // Initial update
    this.updateElements();
  }

  /**
   * Stop listening for scroll events
   */
  public stop(): void {
    window.removeEventListener('scroll', this.handleScroll);
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  /**
   * Handle scroll event with requestAnimationFrame for performance
   */
  private handleScroll(): void {
    this.lastScrollY = window.scrollY;

    if (!this.ticking) {
      this.rafId = requestAnimationFrame(this.updateElements);
      this.ticking = true;
    }
  }

  /**
   * Update all parallax elements based on scroll position
   */
  private updateElements(): void {
    const windowHeight = window.innerHeight;
    const scrolled = this.lastScrollY;

    this.parallaxElements.forEach(({ element, speed, offset }) => {
      const rect = element.getBoundingClientRect();
      const elementTop = rect.top + scrolled;
      const elementHeight = element.offsetHeight;

      // Check if element is in viewport
      const elementBottom = elementTop + elementHeight;
      const viewportBottom = scrolled + windowHeight;

      // Only apply parallax to elements that are visible or near viewport
      if (elementBottom < scrolled - 200 || elementTop > viewportBottom + 200) {
        return; // Skip elements far from viewport
      }

      // Calculate parallax offset based on scroll position
      // Negative speed creates opposite movement (proper parallax)
      // Positive speed creates same-direction movement (for backgrounds)
      const parallaxOffset = -(scrolled * speed) + offset;

      // Apply transform
      this.applyTransform(element, parallaxOffset);
    });

    this.ticking = false;
  }

  /**
   * Apply CSS transform to element
   */
  private applyTransform(element: HTMLElement, offset: number): void {
    element.style.transform = `translate3d(0, ${offset}px, 0)`;
    element.style.willChange = 'transform';
  }

  /**
   * Clear all registered elements
   */
  public clear(): void {
    this.parallaxElements = [];
    this.stop();
  }

  /**
   * Destroy the parallax controller
   */
  public destroy(): void {
    this.clear();
    this.parallaxElements.forEach(({ element }) => {
      element.style.transform = '';
      element.style.willChange = '';
    });
  }
}

// Singleton instance for easy access
let parallaxInstance: ParallaxController | null = null;

export function getParallaxController(): ParallaxController {
  if (!parallaxInstance) {
    parallaxInstance = new ParallaxController();
  }
  return parallaxInstance;
}

export function destroyParallaxController(): void {
  if (parallaxInstance) {
    parallaxInstance.destroy();
    parallaxInstance = null;
  }
}