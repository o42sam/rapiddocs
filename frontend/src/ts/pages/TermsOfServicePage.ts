export class TermsOfServicePage {
  render(): void {
    const app = document.getElementById('app');
    if (!app) return;

    app.innerHTML = `
      <div class="min-h-screen bg-gradient-to-br from-primary-50 via-white to-purple-50 py-12">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <!-- Back Button -->
          <div class="mb-8">
            <a href="/" class="inline-flex items-center text-primary-600 hover:text-primary-700 transition-colors">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Home
            </a>
          </div>

          <!-- Content -->
          <div class="max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-8 md:p-12">
            <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Terms of Service</h1>
            <p class="text-gray-600 mb-8">Last Updated: January 27, 2025</p>

            <div class="prose prose-lg max-w-none">
              <!-- Introduction -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">1. Agreement to Terms</h2>
                <p class="text-gray-700 mb-4">
                  By accessing or using RapidDocs ("the Service", "our Service"), you agree to be bound by these Terms of Service ("Terms"). If you disagree with any part of these terms, you may not access the Service.
                </p>
                <p class="text-gray-700">
                  These Terms apply to all visitors, users, and others who access or use the Service.
                </p>
              </section>

              <!-- Acceptable Use -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">2. Acceptable Use Policy</h2>
                <p class="text-gray-700 mb-4">
                  <strong>You expressly agree not to use the Service for any illegal purposes or activities.</strong> By using RapidDocs, you vow and warrant that:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700 mb-4">
                  <li>You will not use the Service to create, generate, or distribute content that is illegal, fraudulent, defamatory, or harmful</li>
                  <li>You will not use the Service to violate any applicable local, state, national, or international law</li>
                  <li>You will not use the Service to infringe upon the intellectual property rights of others</li>
                  <li>You will not use the Service to create misleading, deceptive, or false documents</li>
                  <li>You will not use the Service to generate content for harassment, spam, or malicious purposes</li>
                  <li>You will not use the Service to create documents that violate export control regulations or sanctions</li>
                  <li>You will not attempt to circumvent any security features or limitations of the Service</li>
                  <li>You will not use the Service to transmit malware, viruses, or any malicious code</li>
                </ul>
                <p class="text-gray-700">
                  We reserve the right to suspend or terminate your account immediately if we determine, in our sole discretion, that you have violated this Acceptable Use Policy.
                </p>
              </section>

              <!-- User Accounts -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">3. User Accounts and Registration</h2>
                <p class="text-gray-700 mb-4">
                  To access certain features of the Service, you may be required to register for an account. You agree to:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700 mb-4">
                  <li>Provide accurate, current, and complete information during registration</li>
                  <li>Maintain and promptly update your account information</li>
                  <li>Maintain the security and confidentiality of your account credentials</li>
                  <li>Accept all responsibility for activities that occur under your account</li>
                  <li>Notify us immediately of any unauthorized use of your account</li>
                </ul>
                <p class="text-gray-700">
                  You are responsible for safeguarding the password you use to access the Service and for any activities or actions under your password.
                </p>
              </section>

              <!-- Service Usage -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">4. Service Usage and Limitations</h2>
                <p class="text-gray-700 mb-4">
                  RapidDocs operates on a credit-based system. Each document generation consumes credits based on:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700 mb-4">
                  <li>Document length and complexity</li>
                  <li>Number of AI-generated images requested</li>
                  <li>Data visualizations and charts included</li>
                  <li>Custom design specifications applied</li>
                </ul>
                <p class="text-gray-700 mb-4">
                  You acknowledge that:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700">
                  <li>Credits are non-refundable once purchased</li>
                  <li>Credits do not expire but may be subject to account inactivity policies</li>
                  <li>We reserve the right to modify credit costs with reasonable notice</li>
                  <li>Service availability is subject to API limitations and system capacity</li>
                </ul>
              </section>

              <!-- Intellectual Property -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">5. Intellectual Property Rights</h2>
                <p class="text-gray-700 mb-4">
                  <strong>Your Content:</strong> You retain all rights to the content you upload to the Service (including company logos, statistics, and document descriptions). By uploading content, you grant us a limited, non-exclusive license to use, process, and display your content solely for the purpose of providing the Service.
                </p>
                <p class="text-gray-700 mb-4">
                  <strong>Generated Documents:</strong> Documents generated by the Service using AI models are provided to you with a non-exclusive license. You are responsible for reviewing and ensuring that generated content meets your requirements and does not infringe third-party rights.
                </p>
                <p class="text-gray-700">
                  <strong>Our Service:</strong> The Service, including its original content, features, functionality, and underlying technology, is owned by RapidDocs and is protected by international copyright, trademark, patent, trade secret, and other intellectual property laws.
                </p>
              </section>

              <!-- AI-Generated Content -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">6. AI-Generated Content Disclaimer</h2>
                <p class="text-gray-700 mb-4">
                  RapidDocs uses third-party AI models (including but not limited to Hugging Face models) to generate text and images. You acknowledge and agree that:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700 mb-4">
                  <li>AI-generated content may contain inaccuracies, errors, or biases</li>
                  <li>You are solely responsible for reviewing and verifying all generated content before use</li>
                  <li>We do not guarantee the accuracy, completeness, or suitability of AI-generated content</li>
                  <li>AI-generated content should not be relied upon for critical business, legal, medical, or financial decisions without professional review</li>
                  <li>Generated images may occasionally contain unexpected or unintended elements</li>
                </ul>
                <p class="text-gray-700">
                  You agree to use AI-generated content responsibly and to comply with all applicable laws and third-party terms of service.
                </p>
              </section>

              <!-- Payment Terms -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">7. Payment and Billing</h2>
                <p class="text-gray-700 mb-4">
                  <strong>Credit Purchases:</strong> Credits can be purchased through our payment processors (including cryptocurrency payment options). All payments are processed securely through third-party payment providers.
                </p>
                <p class="text-gray-700 mb-4">
                  <strong>Pricing:</strong> We reserve the right to modify our pricing at any time. Price changes will not affect credits already purchased.
                </p>
                <p class="text-gray-700">
                  <strong>Refunds:</strong> Due to the nature of digital services and immediate credit delivery, all credit purchases are final and non-refundable, except as required by law or at our sole discretion.
                </p>
              </section>

              <!-- Privacy and Data -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">8. Privacy and Data Protection</h2>
                <p class="text-gray-700 mb-4">
                  Your use of the Service is also governed by our Privacy Policy, which is incorporated into these Terms by reference. Please review our <a href="/privacy-policy" class="text-primary-600 hover:text-primary-700 underline">Privacy Policy</a> to understand our data collection and processing practices.
                </p>
                <p class="text-gray-700">
                  You consent to the collection, processing, and use of your data as described in the Privacy Policy, including the transmission of your data to third-party AI service providers for document generation purposes.
                </p>
              </section>

              <!-- Limitation of Liability -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">9. Limitation of Liability</h2>
                <p class="text-gray-700 mb-4">
                  TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL RAPIDDOCS, ITS DIRECTORS, EMPLOYEES, PARTNERS, AGENTS, SUPPLIERS, OR AFFILIATES BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING WITHOUT LIMITATION:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700 mb-4">
                  <li>Loss of profits, revenue, data, or use</li>
                  <li>Loss of business opportunities</li>
                  <li>Costs of procurement of substitute services</li>
                  <li>Damages arising from reliance on AI-generated content</li>
                </ul>
                <p class="text-gray-700">
                  Our total liability to you for all claims arising from or relating to the Service shall not exceed the amount you paid us in the twelve (12) months preceding the claim, or one hundred dollars ($100), whichever is greater.
                </p>
              </section>

              <!-- Disclaimer of Warranties -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">10. Disclaimer of Warranties</h2>
                <p class="text-gray-700 mb-4">
                  THE SERVICE IS PROVIDED ON AN "AS IS" AND "AS AVAILABLE" BASIS WITHOUT ANY WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700 mb-4">
                  <li>Warranties of merchantability, fitness for a particular purpose, or non-infringement</li>
                  <li>Warranties that the Service will be uninterrupted, secure, or error-free</li>
                  <li>Warranties regarding the accuracy, reliability, or quality of AI-generated content</li>
                  <li>Warranties that defects will be corrected</li>
                </ul>
                <p class="text-gray-700">
                  We do not warrant that the Service will meet your requirements or that any errors in the Service will be corrected.
                </p>
              </section>

              <!-- Third-Party Services -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">11. Third-Party Services and Links</h2>
                <p class="text-gray-700 mb-4">
                  The Service may contain links to third-party websites or services (including Hugging Face AI models, payment processors, and OAuth providers such as Google) that are not owned or controlled by RapidDocs.
                </p>
                <p class="text-gray-700">
                  We have no control over, and assume no responsibility for, the content, privacy policies, or practices of any third-party websites or services. You acknowledge and agree that RapidDocs shall not be responsible or liable for any damage or loss caused by your use of any such third-party services.
                </p>
              </section>

              <!-- Termination -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">12. Termination</h2>
                <p class="text-gray-700 mb-4">
                  We may terminate or suspend your account and access to the Service immediately, without prior notice or liability, for any reason, including without limitation if you breach these Terms.
                </p>
                <p class="text-gray-700 mb-4">
                  Upon termination:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700 mb-4">
                  <li>Your right to use the Service will immediately cease</li>
                  <li>Any unused credits in your account may be forfeited</li>
                  <li>We may delete your account data in accordance with our Privacy Policy</li>
                </ul>
                <p class="text-gray-700">
                  You may terminate your account at any time by contacting us. Termination does not entitle you to a refund of unused credits.
                </p>
              </section>

              <!-- Governing Law -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">13. Governing Law and Jurisdiction</h2>
                <p class="text-gray-700 mb-4">
                  These Terms shall be governed and construed in accordance with the laws of the United States, without regard to its conflict of law provisions.
                </p>
                <p class="text-gray-700">
                  Any disputes arising from these Terms or your use of the Service shall be subject to the exclusive jurisdiction of the courts located in the United States.
                </p>
              </section>

              <!-- Indemnification -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">14. Indemnification</h2>
                <p class="text-gray-700">
                  You agree to defend, indemnify, and hold harmless RapidDocs and its licensees, licensors, employees, contractors, agents, officers, and directors from and against any claims, damages, obligations, losses, liabilities, costs, or expenses arising from:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700 mt-4">
                  <li>Your use of and access to the Service</li>
                  <li>Your violation of these Terms</li>
                  <li>Your violation of any third-party rights, including intellectual property rights</li>
                  <li>Content you upload or generate using the Service</li>
                  <li>Your use of the Service for illegal purposes</li>
                </ul>
              </section>

              <!-- Changes to Terms -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">15. Changes to Terms</h2>
                <p class="text-gray-700 mb-4">
                  We reserve the right to modify or replace these Terms at any time at our sole discretion. If a revision is material, we will provide at least 30 days' notice prior to any new terms taking effect.
                </p>
                <p class="text-gray-700">
                  By continuing to access or use the Service after revisions become effective, you agree to be bound by the revised terms. If you do not agree to the new terms, you must stop using the Service.
                </p>
              </section>

              <!-- Severability -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">16. Severability and Waiver</h2>
                <p class="text-gray-700 mb-4">
                  If any provision of these Terms is held to be unenforceable or invalid, such provision will be changed and interpreted to accomplish the objectives of such provision to the greatest extent possible under applicable law, and the remaining provisions will continue in full force and effect.
                </p>
                <p class="text-gray-700">
                  No waiver by RapidDocs of any term or condition shall be deemed a further or continuing waiver of such term or any other term.
                </p>
              </section>

              <!-- Entire Agreement -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">17. Entire Agreement</h2>
                <p class="text-gray-700">
                  These Terms, together with our Privacy Policy and any other legal notices published by us on the Service, constitute the entire agreement between you and RapidDocs concerning the Service and supersede all prior agreements and understandings.
                </p>
              </section>

              <!-- Contact Information -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">18. Contact Information</h2>
                <p class="text-gray-700 mb-4">
                  If you have any questions about these Terms, please contact us at:
                </p>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <p class="text-gray-700 font-medium">RapidDocs Legal Team</p>
                  <p class="text-gray-700">Email: legal@rapiddocs.com</p>
                  <p class="text-gray-700">Support: support@rapiddocs.com</p>
                </div>
              </section>

              <!-- Acknowledgment -->
              <section class="mb-8 bg-primary-50 p-6 rounded-lg border-l-4 border-primary-600">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">Acknowledgment</h2>
                <p class="text-gray-700">
                  BY USING THE SERVICE, YOU ACKNOWLEDGE THAT YOU HAVE READ THESE TERMS OF SERVICE, UNDERSTAND THEM, AND AGREE TO BE BOUND BY THEM. YOU SPECIFICALLY ACKNOWLEDGE AND AGREE THAT YOU WILL NOT USE THE SERVICE FOR ANY ILLEGAL PURPOSES AND THAT YOU ARE RESPONSIBLE FOR COMPLIANCE WITH ALL APPLICABLE LAWS.
                </p>
              </section>
            </div>
          </div>
        </div>
      </div>
    `;

    // Add click handler for back button
    const backButton = app.querySelector('a[href="/"]');
    if (backButton) {
      backButton.addEventListener('click', (e) => {
        e.preventDefault();
        const { router } = require('../router');
        router.navigate('/');
      });
    }
  }

  destroy(): void {
    // Cleanup if needed
  }
}
