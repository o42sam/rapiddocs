import { ColorTheme, COLOR_THEMES, DesignSpecification } from '../types/document';

export class ColorPalette {
  private container: HTMLElement;
  private selectedTheme: ColorTheme;
  private onChangeCallback?: (spec: DesignSpecification) => void;

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Element with id ${containerId} not found`);
    }
    this.container = element;
    this.selectedTheme = COLOR_THEMES[0]; // Default to Ocean Blue
    this.render();
  }

  onChange(callback: (spec: DesignSpecification) => void): void {
    this.onChangeCallback = callback;
  }

  getSelectedTheme(): DesignSpecification {
    return {
      background_color: this.selectedTheme.background,
      foreground_color_1: this.selectedTheme.foreground1,
      foreground_color_2: this.selectedTheme.foreground2,
      theme_name: this.selectedTheme.name,
    };
  }

  private render(): void {
    this.container.innerHTML = `
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Color Theme
      </label>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        ${COLOR_THEMES.map(
          (theme, index) => `
          <button
            type="button"
            data-theme-index="${index}"
            class="theme-option p-4 border-2 rounded-lg transition-all hover:shadow-lg ${
              index === 0 ? 'border-primary-500 bg-primary-50' : 'border-gray-200'
            }"
          >
            <div class="flex gap-2 mb-2">
              <div class="w-8 h-8 rounded" style="background-color: ${theme.foreground1}"></div>
              <div class="w-8 h-8 rounded" style="background-color: ${theme.foreground2}"></div>
            </div>
            <div class="text-xs font-medium text-gray-700">${theme.name}</div>
          </button>
        `
        ).join('')}
      </div>
    `;

    this.attachEventListeners();
  }

  private attachEventListeners(): void {
    const buttons = this.container.querySelectorAll('.theme-option');
    buttons.forEach((button) => {
      button.addEventListener('click', (e) => {
        const target = e.currentTarget as HTMLElement;
        const index = parseInt(target.dataset.themeIndex || '0');
        this.selectTheme(index);
      });
    });
  }

  private selectTheme(index: number): void {
    this.selectedTheme = COLOR_THEMES[index];

    // Update UI
    const buttons = this.container.querySelectorAll('.theme-option');
    buttons.forEach((button, i) => {
      if (i === index) {
        button.classList.add('border-primary-500', 'bg-primary-50');
        button.classList.remove('border-gray-200');
      } else {
        button.classList.remove('border-primary-500', 'bg-primary-50');
        button.classList.add('border-gray-200');
      }
    });

    // Trigger callback
    if (this.onChangeCallback) {
      this.onChangeCallback(this.getSelectedTheme());
    }
  }
}
