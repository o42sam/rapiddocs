/**
 * Intersection Observer utility for scroll animations
 */

export interface ObserverOptions {
  threshold?: number;
  rootMargin?: string;
  onIntersect?: (entry: IntersectionObserverEntry) => void;
}

export class ScrollAnimationObserver {
  private observer: IntersectionObserver;
  private elements: Set<Element> = new Set();

  constructor(options: ObserverOptions = {}) {
    const {
      threshold = 0.1,
      rootMargin = '0px 0px -100px 0px',
      onIntersect
    } = options;

    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            entry.target.classList.remove('fade-in-bottom');

            if (onIntersect) {
              onIntersect(entry);
            }
          }
        });
      },
      {
        threshold,
        rootMargin
      }
    );
  }

  observe(element: Element): void {
    if (!this.elements.has(element)) {
      this.elements.add(element);
      element.classList.add('fade-in-bottom');
      this.observer.observe(element);
    }
  }

  unobserve(element: Element): void {
    if (this.elements.has(element)) {
      this.elements.delete(element);
      this.observer.unobserve(element);
    }
  }

  disconnect(): void {
    this.observer.disconnect();
    this.elements.clear();
  }
}

// Initialize scroll animations
export function initScrollAnimations(): ScrollAnimationObserver {
  const observer = new ScrollAnimationObserver({
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  });

  // Observe all elements with data-animate attribute
  document.querySelectorAll('[data-animate]').forEach((el) => {
    observer.observe(el);
  });

  return observer;
}
