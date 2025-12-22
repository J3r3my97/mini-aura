'use client';

export default function Privacy() {
  return (
    <div className="min-h-screen bg-[#e6e7f0] py-20">
      <div className="container mx-auto px-6 max-w-4xl">
        <h1 className="text-5xl font-bold mb-8">Privacy Policy</h1>
        <p className="text-sm text-[#7a7a8e] mb-12">Last updated: December 2024</p>

        <div className="neu-card rounded-3xl p-8 space-y-6">
          <section>
            <h2 className="text-2xl font-bold mb-4">1. Information We Collect</h2>

            <h3 className="text-xl font-semibold mb-3 text-[#8b7fc7]">Account Information</h3>
            <p className="text-[#4a4a5e] mb-3">
              When you create an account, we collect:
            </p>
            <ul className="list-disc list-inside text-[#4a4a5e] space-y-2 ml-4 mb-4">
              <li>Email address</li>
              <li>Authentication credentials (managed by Firebase)</li>
              <li>Account creation date</li>
            </ul>

            <h3 className="text-xl font-semibold mb-3 text-[#8b7fc7]">Usage Data</h3>
            <p className="text-[#4a4a5e] mb-3">
              We collect information about how you use the Service:
            </p>
            <ul className="list-disc list-inside text-[#4a4a5e] space-y-2 ml-4 mb-4">
              <li>Number of avatars generated</li>
              <li>Credit purchases and usage</li>
              <li>Generation history</li>
            </ul>

            <h3 className="text-xl font-semibold mb-3 text-[#8b7fc7]">Uploaded Content</h3>
            <p className="text-[#4a4a5e]">
              Images you upload are temporarily stored to generate your pixel art avatar. We process these images using AI models and store both the input and generated output.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">2. How We Use Your Information</h2>
            <p className="text-[#4a4a5e] mb-3">
              We use the collected information to:
            </p>
            <ul className="list-disc list-inside text-[#4a4a5e] space-y-2 ml-4">
              <li>Provide and maintain the avatar generation service</li>
              <li>Process your credit purchases through Stripe</li>
              <li>Track credit usage and enforce limits</li>
              <li>Improve our AI models and service quality</li>
              <li>Send important service updates and notifications</li>
              <li>Respond to support requests</li>
              <li>Prevent fraud and abuse</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">3. Data Storage and Security</h2>
            <p className="text-[#4a4a5e] mb-3">
              <strong>Storage Location:</strong> Your data is stored on Google Cloud Platform (GCP) servers in the United States.
            </p>
            <p className="text-[#4a4a5e] mb-3">
              <strong>Security Measures:</strong> We implement industry-standard security measures including encryption, secure authentication, and access controls.
            </p>
            <p className="text-[#4a4a5e]">
              <strong>Data Retention:</strong> We retain your uploaded images and generated avatars for a reasonable period. You can request deletion of your data at any time.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">4. Third-Party Services</h2>

            <h3 className="text-xl font-semibold mb-3 text-[#8b7fc7]">Firebase (Google)</h3>
            <p className="text-[#4a4a5e] mb-3">
              We use Firebase for authentication and database services. Firebase collects and processes data according to Google's Privacy Policy.
            </p>

            <h3 className="text-xl font-semibold mb-3 text-[#8b7fc7]">Stripe</h3>
            <p className="text-[#4a4a5e] mb-3">
              Payment processing is handled by Stripe. We do not store your credit card information. Stripe's Privacy Policy governs how they handle payment data.
            </p>

            <h3 className="text-xl font-semibold mb-3 text-[#8b7fc7]">Google Cloud Platform</h3>
            <p className="text-[#4a4a5e] mb-3">
              We use GCP for hosting, storage, and AI processing. Your images are processed using Google's AI services.
            </p>

            <h3 className="text-xl font-semibold mb-3 text-[#8b7fc7]">OpenAI</h3>
            <p className="text-[#4a4a5e]">
              Some avatar generation uses OpenAI's DALL-E API. Images sent to OpenAI are subject to their Privacy Policy and data retention practices.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">5. Cookies and Tracking</h2>
            <p className="text-[#4a4a5e] mb-3">
              We use essential cookies for:
            </p>
            <ul className="list-disc list-inside text-[#4a4a5e] space-y-2 ml-4">
              <li>Authentication and session management</li>
              <li>Remembering your preferences</li>
              <li>Security and fraud prevention</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">6. Data Sharing</h2>
            <p className="text-[#4a4a5e] mb-3">
              We do not sell your personal information. We may share data with:
            </p>
            <ul className="list-disc list-inside text-[#4a4a5e] space-y-2 ml-4">
              <li>Service providers necessary to operate the Service (Firebase, Stripe, GCP, OpenAI)</li>
              <li>Law enforcement when required by law</li>
              <li>Business partners with your explicit consent</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">7. Your Rights</h2>
            <p className="text-[#4a4a5e] mb-3">
              You have the right to:
            </p>
            <ul className="list-disc list-inside text-[#4a4a5e] space-y-2 ml-4">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Correction:</strong> Update or correct your information</li>
              <li><strong>Deletion:</strong> Request deletion of your account and data</li>
              <li><strong>Data Portability:</strong> Export your generated avatars</li>
              <li><strong>Opt-out:</strong> Unsubscribe from marketing communications</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">8. Children's Privacy</h2>
            <p className="text-[#4a4a5e]">
              The Service is not intended for children under 13. We do not knowingly collect data from children under 13. If we learn we have collected such data, we will delete it promptly.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">9. International Users</h2>
            <p className="text-[#4a4a5e]">
              If you access the Service from outside the United States, your data will be transferred to and processed in the United States. By using the Service, you consent to this transfer.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">10. Changes to Privacy Policy</h2>
            <p className="text-[#4a4a5e]">
              We may update this Privacy Policy from time to time. We will notify you of significant changes by email or through the Service. Continued use after changes constitutes acceptance.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">11. Contact Us</h2>
            <p className="text-[#4a4a5e] mb-3">
              For privacy-related questions or to exercise your rights, please contact us through our website.
            </p>
            <p className="text-[#4a4a5e]">
              You may also contact us to request deletion of your data or to opt-out of certain data processing activities.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">12. GDPR Compliance (EU Users)</h2>
            <p className="text-[#4a4a5e] mb-3">
              If you are in the European Union, you have additional rights under GDPR:
            </p>
            <ul className="list-disc list-inside text-[#4a4a5e] space-y-2 ml-4">
              <li>Right to be forgotten</li>
              <li>Right to restrict processing</li>
              <li>Right to object to processing</li>
              <li>Right to lodge a complaint with a supervisory authority</li>
            </ul>
          </section>
        </div>

        <div className="mt-8 text-center">
          <a href="/" className="neu-button">
            Back to Home
          </a>
        </div>
      </div>
    </div>
  );
}
