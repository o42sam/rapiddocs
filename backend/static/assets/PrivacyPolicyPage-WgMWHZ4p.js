class i{render(){const t=document.getElementById("app");if(!t)return;t.innerHTML=`
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
            <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
            <p class="text-gray-600 mb-8">Last Updated: January 27, 2025</p>

            <div class="prose prose-lg max-w-none">
              <!-- Introduction -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">1. Introduction</h2>
                <p class="text-gray-700 mb-4">
                  RapidDocs ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our document generation service.
                </p>
                <p class="text-gray-700 mb-4">
                  <strong>This policy provides full transparency about all data used by our application.</strong> By using RapidDocs, you consent to the data practices described in this policy.
                </p>
                <p class="text-gray-700">
                  If you do not agree with the terms of this Privacy Policy, please do not access or use the Service.
                </p>
              </section>

              <!-- Data We Collect -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">2. Data We Collect</h2>
                <p class="text-gray-700 mb-4">
                  We collect and process the following categories of data when you use RapidDocs:
                </p>

                <!-- Account Information -->
                <div class="mb-6">
                  <h3 class="text-xl font-semibold text-gray-900 mb-3">2.1 Account and Authentication Data</h3>
                  <ul class="list-disc pl-6 space-y-2 text-gray-700">
                    <li><strong>Email address:</strong> Used for account creation, authentication, and communication</li>
                    <li><strong>Password:</strong> Stored in hashed and encrypted form for account security</li>
                    <li><strong>Google OAuth data:</strong> If you sign in with Google, we receive:
                      <ul class="list-circle pl-6 mt-2 space-y-1">
                        <li>Google account ID (unique identifier)</li>
                        <li>Email address</li>
                        <li>Profile name</li>
                        <li>Profile picture URL (if available)</li>
                      </ul>
                    </li>
                    <li><strong>Account creation date:</strong> Timestamp of when you registered</li>
                    <li><strong>Last login date:</strong> Timestamp of your most recent login</li>
                  </ul>
                </div>

                <!-- Document Content Data -->
                <div class="mb-6">
                  <h3 class="text-xl font-semibold text-gray-900 mb-3">2.2 Document Content and Generation Data</h3>
                  <p class="text-gray-700 mb-2">When you generate documents, we collect and process:</p>
                  <ul class="list-disc pl-6 space-y-2 text-gray-700">
                    <li><strong>Document descriptions:</strong> The text prompts you provide to describe the document you want to generate</li>
                    <li><strong>Document length specifications:</strong> Your requested word count (500-5,000 words)</li>
                    <li><strong>Company logos:</strong> Image files you upload for branding (PNG, JPG, SVG format)
                      <ul class="list-circle pl-6 mt-2 space-y-1">
                        <li>File name, size, and format</li>
                        <li>Image content and metadata</li>
                      </ul>
                    </li>
                    <li><strong>Company statistics:</strong> Data you provide for visualization, including:
                      <ul class="list-circle pl-6 mt-2 space-y-1">
                        <li>Statistic names and labels</li>
                        <li>Numerical values</li>
                        <li>Units of measurement</li>
                        <li>Selected visualization types (bar, line, pie, gauge charts)</li>
                      </ul>
                    </li>
                    <li><strong>Design specifications:</strong> Your color theme choices:
                      <ul class="list-circle pl-6 mt-2 space-y-1">
                        <li>Background color</li>
                        <li>Primary foreground color</li>
                        <li>Secondary foreground color</li>
                        <li>Theme name (if using preset themes)</li>
                      </ul>
                    </li>
                    <li><strong>Generated PDF documents:</strong> The final PDF files created by our service</li>
                    <li><strong>AI-generated text content:</strong> The document content produced by AI models</li>
                    <li><strong>AI-generated images:</strong> Visual elements created for your documents</li>
                    <li><strong>Data visualizations:</strong> Charts and graphs generated from your statistics</li>
                    <li><strong>Document metadata:</strong> Title, creation date, file size, generation parameters</li>
                  </ul>
                </div>

                <!-- Credit and Payment Data -->
                <div class="mb-6">
                  <h3 class="text-xl font-semibold text-gray-900 mb-3">2.3 Credits and Payment Information</h3>
                  <ul class="list-disc pl-6 space-y-2 text-gray-700">
                    <li><strong>Credit balance:</strong> Current number of credits in your account</li>
                    <li><strong>Credit transaction history:</strong> Records of credits purchased and consumed</li>
                    <li><strong>Purchase amounts:</strong> Dollar amounts for credit purchases</li>
                    <li><strong>Payment method information:</strong> We do NOT directly store credit card numbers or cryptocurrency private keys. Payment processing is handled by third-party processors:
                      <ul class="list-circle pl-6 mt-2 space-y-1">
                        <li>For cryptocurrency payments: Bitcoin wallet addresses (yours and ours), transaction IDs</li>
                        <li>For other payment methods: Data is processed by our payment gateway providers</li>
                      </ul>
                    </li>
                    <li><strong>Transaction timestamps:</strong> Date and time of purchases and credit usage</li>
                  </ul>
                </div>

                <!-- Technical Data -->
                <div class="mb-6">
                  <h3 class="text-xl font-semibold text-gray-900 mb-3">2.4 Technical and Usage Data</h3>
                  <ul class="list-disc pl-6 space-y-2 text-gray-700">
                    <li><strong>IP address:</strong> Your internet protocol address for security and analytics</li>
                    <li><strong>Browser information:</strong> Browser type, version, and user agent string</li>
                    <li><strong>Device information:</strong> Operating system, device type, screen resolution</li>
                    <li><strong>Session data:</strong> Authentication tokens, session duration, session IDs</li>
                    <li><strong>Cookies and local storage:</strong> Authentication tokens, user preferences, temporary data</li>
                    <li><strong>Usage statistics:</strong> Pages visited, features used, document generation frequency</li>
                    <li><strong>Error logs:</strong> Technical errors and crash reports for debugging</li>
                    <li><strong>API request logs:</strong> Timestamps and types of API calls made</li>
                  </ul>
                </div>

                <!-- Communications -->
                <div class="mb-6">
                  <h3 class="text-xl font-semibold text-gray-900 mb-3">2.5 Communications Data</h3>
                  <ul class="list-disc pl-6 space-y-2 text-gray-700">
                    <li><strong>Support inquiries:</strong> Messages you send to customer support</li>
                    <li><strong>Email communications:</strong> Records of emails sent to and from you</li>
                    <li><strong>Feedback and surveys:</strong> Any feedback or survey responses you provide</li>
                  </ul>
                </div>
              </section>

              <!-- How We Use Your Data -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">3. How We Use Your Data</h2>
                <p class="text-gray-700 mb-4">We use the collected data for the following purposes:</p>

                <div class="space-y-4">
                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">3.1 Service Provision</h4>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li>Generate professional PDF documents based on your specifications</li>
                      <li>Process document descriptions through AI text generation models</li>
                      <li>Create custom visualizations from your statistics</li>
                      <li>Apply your branding (logo and color themes) to documents</li>
                      <li>Store and retrieve your generated documents</li>
                    </ul>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">3.2 Account Management</h4>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li>Authenticate and authorize access to your account</li>
                      <li>Manage your credit balance and transaction history</li>
                      <li>Process credit purchases and payments</li>
                      <li>Provide access to your document history</li>
                    </ul>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">3.3 Service Improvement</h4>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li>Analyze usage patterns to improve features</li>
                      <li>Monitor service performance and reliability</li>
                      <li>Debug and resolve technical issues</li>
                      <li>Develop new features based on user needs</li>
                    </ul>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">3.4 Security and Fraud Prevention</h4>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li>Detect and prevent unauthorized access</li>
                      <li>Identify and prevent fraudulent transactions</li>
                      <li>Monitor for abuse of the service</li>
                      <li>Enforce our Terms of Service</li>
                    </ul>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">3.5 Communications</h4>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li>Send transactional emails (account verification, password resets, purchase confirmations)</li>
                      <li>Respond to support inquiries</li>
                      <li>Notify you of service updates or changes (with your consent)</li>
                    </ul>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">3.6 Legal Compliance</h4>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li>Comply with applicable laws and regulations</li>
                      <li>Respond to legal requests from authorities</li>
                      <li>Protect our legal rights and enforce our agreements</li>
                    </ul>
                  </div>
                </div>
              </section>

              <!-- Data Sharing -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">4. How We Share Your Data</h2>
                <p class="text-gray-700 mb-4">
                  <strong>We do not sell your personal data to third parties.</strong> However, we share your data with the following categories of third parties:
                </p>

                <div class="space-y-4">
                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">4.1 AI Service Providers (Hugging Face)</h4>
                    <p class="text-gray-700 mb-2">
                      We transmit the following data to Hugging Face API for document generation:
                    </p>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li>Your document descriptions and prompts (for text generation)</li>
                      <li>Image generation prompts derived from your specifications</li>
                      <li>Context about desired length and structure</li>
                    </ul>
                    <p class="text-gray-700 mt-2">
                      <strong>Important:</strong> Hugging Face processes this data to generate content. Please review Hugging Face's privacy policy at <a href="https://huggingface.co/privacy" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 underline">https://huggingface.co/privacy</a>
                    </p>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">4.2 Authentication Providers (Google OAuth)</h4>
                    <p class="text-gray-700 mb-2">
                      If you sign in with Google, we interact with Google's OAuth service:
                    </p>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li>Google provides us with your account ID, email, name, and profile picture</li>
                      <li>We send authentication requests to Google's servers</li>
                      <li>Google's privacy policy applies: <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 underline">https://policies.google.com/privacy</a></li>
                    </ul>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">4.3 Payment Processors</h4>
                    <p class="text-gray-700 mb-2">
                      We share payment-related data with:
                    </p>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li><strong>Cryptocurrency payment processors:</strong> Bitcoin wallet addresses and transaction amounts</li>
                      <li><strong>Traditional payment gateways:</strong> Purchase amounts and transaction references (no full card details stored by us)</li>
                    </ul>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">4.4 Database and Hosting Providers (MongoDB Atlas)</h4>
                    <p class="text-gray-700 mb-2">
                      All your account data, documents, and metadata are stored in MongoDB Atlas:
                    </p>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li>MongoDB Atlas hosts our database infrastructure</li>
                      <li>Data is encrypted in transit and at rest</li>
                      <li>MongoDB's privacy policy: <a href="https://www.mongodb.com/legal/privacy-policy" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 underline">https://www.mongodb.com/legal/privacy-policy</a></li>
                    </ul>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">4.5 Cloud Storage Providers</h4>
                    <p class="text-gray-700 mb-2">
                      We may store uploaded files and generated documents on:
                    </p>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li>Local server storage (encrypted)</li>
                      <li>AWS S3 or similar cloud storage (if configured)</li>
                    </ul>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">4.6 Analytics and Monitoring Services</h4>
                    <p class="text-gray-700">
                      We may use analytics services to monitor service performance and usage. These services receive anonymized or pseudonymized usage data.
                    </p>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">4.7 Legal and Regulatory Authorities</h4>
                    <p class="text-gray-700">
                      We may disclose your data if required by law, court order, or governmental regulation, or to protect our rights and safety.
                    </p>
                  </div>
                </div>
              </section>

              <!-- Data Security -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">5. Data Security</h2>
                <p class="text-gray-700 mb-4">
                  We implement industry-standard security measures to protect your data:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700">
                  <li><strong>Encryption in transit:</strong> All data transmitted between your browser and our servers uses HTTPS/TLS encryption</li>
                  <li><strong>Encryption at rest:</strong> Sensitive data in our database is encrypted</li>
                  <li><strong>Password hashing:</strong> Passwords are hashed using bcrypt with salt</li>
                  <li><strong>Access controls:</strong> Strict access controls limit who can access user data</li>
                  <li><strong>Regular security audits:</strong> We conduct security reviews and vulnerability assessments</li>
                  <li><strong>Secure API communication:</strong> Authentication tokens for API requests</li>
                </ul>
                <p class="text-gray-700 mt-4">
                  However, no method of transmission over the Internet or electronic storage is 100% secure. While we strive to use commercially acceptable means to protect your data, we cannot guarantee absolute security.
                </p>
              </section>

              <!-- Data Retention -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">6. Data Retention</h2>
                <p class="text-gray-700 mb-4">
                  We retain your data for the following periods:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700">
                  <li><strong>Account data:</strong> Retained while your account is active and for 90 days after account closure</li>
                  <li><strong>Generated documents:</strong> Stored indefinitely while your account is active; deleted 30 days after account closure</li>
                  <li><strong>Payment records:</strong> Retained for 7 years for legal and tax compliance</li>
                  <li><strong>Usage logs:</strong> Retained for 12 months for security and analytics</li>
                  <li><strong>Support communications:</strong> Retained for 3 years</li>
                </ul>
                <p class="text-gray-700 mt-4">
                  You may request earlier deletion of your data by contacting us, subject to legal requirements.
                </p>
              </section>

              <!-- Your Rights -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">7. Your Privacy Rights</h2>
                <p class="text-gray-700 mb-4">
                  Depending on your location, you may have the following rights:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700">
                  <li><strong>Right to access:</strong> Request a copy of the personal data we hold about you</li>
                  <li><strong>Right to rectification:</strong> Request correction of inaccurate or incomplete data</li>
                  <li><strong>Right to erasure:</strong> Request deletion of your personal data ("right to be forgotten")</li>
                  <li><strong>Right to data portability:</strong> Receive your data in a structured, machine-readable format</li>
                  <li><strong>Right to restrict processing:</strong> Request that we limit how we use your data</li>
                  <li><strong>Right to object:</strong> Object to processing of your data for certain purposes</li>
                  <li><strong>Right to withdraw consent:</strong> Withdraw previously given consent at any time</li>
                  <li><strong>Right to lodge a complaint:</strong> File a complaint with your local data protection authority</li>
                </ul>
                <p class="text-gray-700 mt-4">
                  To exercise these rights, please contact us at <strong>privacy@rapiddocs.com</strong>. We will respond to your request within 30 days.
                </p>
              </section>

              <!-- Cookies -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">8. Cookies and Tracking Technologies</h2>
                <p class="text-gray-700 mb-4">
                  We use the following cookies and similar technologies:
                </p>
                <div class="space-y-4">
                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">8.1 Essential Cookies</h4>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li><strong>Authentication tokens:</strong> Keep you logged in (stored in localStorage)</li>
                      <li><strong>Session cookies:</strong> Maintain your session state</li>
                      <li><strong>CSRF tokens:</strong> Protect against cross-site request forgery</li>
                    </ul>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">8.2 Preference Cookies</h4>
                    <ul class="list-disc pl-6 space-y-1 text-gray-700">
                      <li><strong>UI preferences:</strong> Remember your color theme and layout preferences</li>
                      <li><strong>Language settings:</strong> Store your language preference</li>
                    </ul>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">8.3 Analytics Cookies</h4>
                    <p class="text-gray-700">
                      We may use analytics cookies to understand how users interact with our service. You can opt out of analytics tracking through your browser settings.
                    </p>
                  </div>
                </div>
                <p class="text-gray-700 mt-4">
                  You can control cookies through your browser settings. However, disabling essential cookies may affect service functionality.
                </p>
              </section>

              <!-- International Transfers -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">9. International Data Transfers</h2>
                <p class="text-gray-700 mb-4">
                  Your data may be transferred to and processed in countries other than your own, including:
                </p>
                <ul class="list-disc pl-6 space-y-2 text-gray-700">
                  <li>United States (our primary servers and MongoDB Atlas databases)</li>
                  <li>Locations where Hugging Face operates AI model inference servers</li>
                  <li>Locations where our third-party service providers operate</li>
                </ul>
                <p class="text-gray-700 mt-4">
                  We ensure appropriate safeguards are in place for international data transfers, including standard contractual clauses and adequacy decisions.
                </p>
              </section>

              <!-- Children's Privacy -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">10. Children's Privacy</h2>
                <p class="text-gray-700">
                  Our Service is not intended for users under the age of 18. We do not knowingly collect personal data from children. If we discover that we have collected data from a child, we will delete it immediately. If you believe we have collected data from a child, please contact us at <strong>privacy@rapiddocs.com</strong>.
                </p>
              </section>

              <!-- Changes to Policy -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">11. Changes to This Privacy Policy</h2>
                <p class="text-gray-700 mb-4">
                  We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated "Last Updated" date.
                </p>
                <p class="text-gray-700">
                  For material changes, we will notify you by email or through a prominent notice on our Service at least 30 days before the changes take effect. Your continued use of the Service after changes become effective constitutes acceptance of the revised policy.
                </p>
              </section>

              <!-- Contact Information -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">12. Contact Us</h2>
                <p class="text-gray-700 mb-4">
                  If you have questions or concerns about this Privacy Policy or our data practices, please contact us:
                </p>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <p class="text-gray-700 font-medium">RapidDocs Privacy Team</p>
                  <p class="text-gray-700">Email: privacy@rapiddocs.com</p>
                  <p class="text-gray-700">Data Protection Officer: dpo@rapiddocs.com</p>
                  <p class="text-gray-700">Support: support@rapiddocs.com</p>
                </div>
              </section>

              <!-- Summary of Data Usage -->
              <section class="mb-8 bg-primary-50 p-6 rounded-lg border-l-4 border-primary-600">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">Summary: All Data Used by RapidDocs</h2>
                <p class="text-gray-700 mb-4">
                  <strong>For complete transparency, here is a comprehensive list of ALL data we collect and use:</strong>
                </p>
                <div class="space-y-3 text-gray-700">
                  <p><strong>Identity Data:</strong> Email, password (hashed), Google OAuth ID, name, profile picture</p>
                  <p><strong>Document Data:</strong> Text prompts, word counts, uploaded logos, statistics (names/values/units), color themes, generated PDFs, AI-generated text/images, visualizations</p>
                  <p><strong>Financial Data:</strong> Credit balance, transaction history, payment amounts, Bitcoin addresses, transaction IDs</p>
                  <p><strong>Technical Data:</strong> IP address, browser/device info, session data, cookies, localStorage, error logs, API logs</p>
                  <p><strong>Usage Data:</strong> Pages visited, features used, generation frequency, timestamps</p>
                  <p><strong>Communication Data:</strong> Support messages, emails, feedback</p>
                </div>
                <p class="text-gray-700 mt-4 font-medium">
                  This data is shared with: Hugging Face (AI processing), Google (OAuth), MongoDB Atlas (database), payment processors, and cloud storage providers.
                </p>
              </section>

              <!-- GDPR & CCPA -->
              <section class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4">13. GDPR and CCPA Compliance</h2>
                <div class="space-y-4">
                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">For EU Users (GDPR)</h4>
                    <p class="text-gray-700">
                      We comply with the General Data Protection Regulation (GDPR). You have enhanced rights including data portability, the right to be forgotten, and the right to object to automated decision-making.
                    </p>
                  </div>
                  <div>
                    <h4 class="font-semibold text-gray-900 mb-2">For California Users (CCPA)</h4>
                    <p class="text-gray-700">
                      We comply with the California Consumer Privacy Act (CCPA). California residents have the right to know what personal information is collected, to delete personal information, and to opt-out of the sale of personal information (note: we do not sell personal information).
                    </p>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    `;const e=t.querySelector('a[href="/"]');e&&e.addEventListener("click",s=>{s.preventDefault();const{router:o}=require("../router");o.navigate("/")})}destroy(){}}export{i as PrivacyPolicyPage};
