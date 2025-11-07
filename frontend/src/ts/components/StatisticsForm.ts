import { Statistic } from '../types/document';
import { validateStatistic } from '../utils/validation';

export class StatisticsForm {
  private container: HTMLElement;
  private statistics: Statistic[] = [];
  private nextId = 1;

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Element with id ${containerId} not found`);
    }
    this.container = element;
    this.render();
  }

  getStatistics(): Statistic[] {
    return this.statistics;
  }

  private render(): void {
    this.container.innerHTML = `
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <label class="block text-sm font-medium text-gray-700">
            Company Statistics (Optional, max 10)
          </label>
          <button
            type="button"
            id="add-statistic-btn"
            class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition disabled:bg-gray-400"
            ${this.statistics.length >= 10 ? 'disabled' : ''}
          >
            + Add Statistic
          </button>
        </div>
        <div id="statistics-list" class="space-y-3">
          ${
            this.statistics.length === 0
              ? '<p class="text-sm text-gray-500 italic">No statistics added yet</p>'
              : this.statistics.map((stat) => this.renderStatistic(stat)).join('')
          }
        </div>
      </div>
    `;

    this.attachEventListeners();
  }

  private renderStatistic(stat: Statistic): string {
    return `
      <div class="statistic-item p-4 border border-gray-200 rounded-lg bg-gray-50" data-id="${stat.id}">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Name</label>
            <input
              type="text"
              class="stat-name w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              value="${stat.name}"
              placeholder="e.g., Revenue Growth"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Value</label>
            <input
              type="number"
              class="stat-value w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              value="${stat.value}"
              step="0.01"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Unit</label>
            <input
              type="text"
              class="stat-unit w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              value="${stat.unit || ''}"
              placeholder="e.g., %, $M"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Chart Type</label>
            <div class="flex gap-2 items-center">
              <select class="stat-viz-type flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm">
                <option value="bar" ${stat.visualization_type === 'bar' ? 'selected' : ''}>Bar</option>
                <option value="line" ${stat.visualization_type === 'line' ? 'selected' : ''}>Line</option>
                <option value="pie" ${stat.visualization_type === 'pie' ? 'selected' : ''}>Pie</option>
                <option value="gauge" ${stat.visualization_type === 'gauge' ? 'selected' : ''}>Gauge</option>
              </select>
              <button
                type="button"
                class="remove-stat-btn px-2 py-2 text-red-600 hover:bg-red-50 rounded transition"
                title="Remove"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  private attachEventListeners(): void {
    const addBtn = document.getElementById('add-statistic-btn');
    if (addBtn) {
      addBtn.addEventListener('click', () => this.addStatistic());
    }

    const listContainer = document.getElementById('statistics-list');
    if (listContainer) {
      listContainer.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        if (target.closest('.remove-stat-btn')) {
          const item = target.closest('.statistic-item') as HTMLElement;
          if (item) {
            this.removeStatistic(item.dataset.id || '');
          }
        }
      });

      listContainer.addEventListener('input', (e) => {
        const target = e.target as HTMLInputElement;
        if (target.closest('.statistic-item')) {
          this.updateStatistics();
        }
      });
    }
  }

  private addStatistic(): void {
    if (this.statistics.length >= 10) {
      return;
    }

    const newStat: Statistic = {
      id: `stat-${this.nextId++}`,
      name: '',
      value: 0,
      unit: '',
      visualization_type: 'bar',
    };

    this.statistics.push(newStat);
    this.render();
  }

  private removeStatistic(id: string): void {
    this.statistics = this.statistics.filter((s) => s.id !== id);
    this.render();
  }

  private updateStatistics(): void {
    const items = this.container.querySelectorAll('.statistic-item');
    items.forEach((item) => {
      const id = (item as HTMLElement).dataset.id;
      const stat = this.statistics.find((s) => s.id === id);
      if (stat) {
        const nameInput = item.querySelector('.stat-name') as HTMLInputElement;
        const valueInput = item.querySelector('.stat-value') as HTMLInputElement;
        const unitInput = item.querySelector('.stat-unit') as HTMLInputElement;
        const vizSelect = item.querySelector('.stat-viz-type') as HTMLSelectElement;

        stat.name = nameInput.value;
        stat.value = parseFloat(valueInput.value) || 0;
        stat.unit = unitInput.value || undefined;
        stat.visualization_type = vizSelect.value as Statistic['visualization_type'];
      }
    });
  }

  validate(): string[] {
    const errors: string[] = [];
    this.updateStatistics();

    this.statistics.forEach((stat, index) => {
      const error = validateStatistic(stat.name, stat.value, stat.unit);
      if (error) {
        errors.push(`Statistic ${index + 1}: ${error}`);
      }
    });

    return errors;
  }
}
