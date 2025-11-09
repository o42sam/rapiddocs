import { router } from '../router';

export class AboutDeveloperPage {
  render(): void {
    const app = document.getElementById('app');
    if (!app) return;

    app.innerHTML = `
      <div class="min-h-screen bg-gray-50 pt-20 pb-12">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="bg-white rounded-xl shadow-lg p-8 md:p-12">
            <h1 class="text-4xl font-bold text-gray-900 mb-6">About the Developer</h1>

            <div class="prose prose-lg max-w-none">
              <p class="text-gray-600 mb-6">
                Built with passion by developers who understand the pain of creating professional documents manually.
                We've leveraged cutting-edge AI technology to automate the entire process.
              </p>

              <p class="text-gray-600 mb-6">
                Our team combines expertise in machine learning, design, and document generation to deliver
                a product that saves you time while maintaining professional quality.
              </p>

              <h2 class="text-2xl font-bold text-gray-900 mt-8 mb-4">Our Mission</h2>
              <p class="text-gray-600 mb-6">
                To democratize professional document creation by making AI-powered tools accessible to everyone,
                regardless of their technical background or design skills.
              </p>

              <h2 class="text-2xl font-bold text-gray-900 mt-8 mb-4">Technology Stack</h2>
              <ul class="list-disc list-inside text-gray-600 mb-6">
                <li>FastAPI for high-performance backend</li>
                <li>Hugging Face AI models for content generation</li>
                <li>MongoDB Atlas for scalable data storage</li>
                <li>TypeScript and Tailwind CSS for modern UI</li>
              </ul>

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
