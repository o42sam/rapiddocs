import { router } from '../router';

export class AboutProductPage {
  render(): void {
    const app = document.getElementById('app');
    if (!app) return;

    app.innerHTML = `
      <div class="min-h-screen bg-gray-50 pt-20 pb-12">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="bg-white rounded-xl shadow-lg p-8 md:p-12">
            <h1 class="text-4xl font-bold text-gray-900 mb-6">About DocGen</h1>

            <div class="prose prose-lg max-w-none">
              <p class="text-gray-600 mb-6">
                DocGen is an AI-powered document generation platform that transforms your ideas into
                professional PDFs with custom branding and data visualizations.
              </p>

              <p class="text-gray-600 mb-6">
                Whether you need business reports, marketing materials, or data-driven presentations,
                DocGen handles everything from content creation to final formatting.
              </p>

              <h2 class="text-2xl font-bold text-gray-900 mt-8 mb-4">Key Features</h2>
              <ul class="list-disc list-inside text-gray-600 mb-6">
                <li>AI-powered content generation using state-of-the-art language models</li>
                <li>Custom branding with logo upload and color theme selection</li>
                <li>Automatic data visualization for statistics and metrics</li>
                <li>Multiple document types: formal reports and infographics</li>
                <li>High-quality PDF output ready for printing or sharing</li>
                <li>Fast generation times (60-120 seconds)</li>
              </ul>

              <h2 class="text-2xl font-bold text-gray-900 mt-8 mb-4">How It Works</h2>
              <ol class="list-decimal list-inside text-gray-600 mb-6 space-y-2">
                <li>Describe your document and specify the length</li>
                <li>Upload your company logo and choose a color theme</li>
                <li>Add statistics and select visualization types</li>
                <li>Click generate and wait while AI creates your document</li>
                <li>Download your professional PDF</li>
              </ol>

              <div class="mt-8">
                <button
                  id="back-home-btn"
                  class="btn-primary"
                >
                  Back to Home
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    this.attachEventListeners();
  }

  private attachEventListeners(): void {
    const backBtn = document.getElementById('back-home-btn');
    if (backBtn) {
      backBtn.addEventListener('click', () => {
        router.navigate('/');
      });
    }
  }
}
