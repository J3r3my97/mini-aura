'use client';

export default function Terms() {
  return (
    <div className="min-h-screen bg-[#e6e7f0] py-20">
      <div className="container mx-auto px-6 max-w-4xl">
        <h1 className="text-5xl font-bold mb-8">Terms of Service</h1>
        <p className="text-sm text-[#7a7a8e] mb-12">Last updated: December 2024</p>

        <div className="neu-card rounded-3xl p-8 space-y-6">
          <section>
            <h2 className="text-2xl font-bold mb-4">1. Acceptance of Terms</h2>
            <p className="text-[#4a4a5e]">
              By accessing and using Mini-Aura ("the Service"), you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to these Terms of Service, please do not use the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">2. Description of Service</h2>
            <p className="text-[#4a4a5e] mb-3">
              Mini-Aura provides an AI-powered pixel art avatar generation service. Users can:
            </p>
            <ul className="list-disc list-inside text-[#4a4a5e] space-y-2 ml-4">
              <li>Upload photos to generate pixel art avatars</li>
              <li>Receive 1 free avatar generation with watermark</li>
              <li>Purchase credits for additional avatar generations without watermark</li>
              <li>Customize and download generated avatars</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">3. Credits and Payment</h2>
            <p className="text-[#4a4a5e] mb-3">
              <strong>Free Credits:</strong> Each new user receives 1 free credit. Avatars generated with free credits include a watermark.
            </p>
            <p className="text-[#4a4a5e] mb-3">
              <strong>Paid Credits:</strong> Users may purchase credit packages through our payment processor (Stripe). Paid credits generate avatars without watermarks.
            </p>
            <p className="text-[#4a4a5e] mb-3">
              <strong>Non-Refundable:</strong> All credit purchases are final and non-refundable. Credits do not expire.
            </p>
            <p className="text-[#4a4a5e]">
              <strong>One Credit = One Avatar:</strong> Each avatar generation consumes one credit.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">4. User Content and Uploads</h2>
            <p className="text-[#4a4a5e] mb-3">
              <strong>Your Responsibility:</strong> You are solely responsible for the content you upload. You must own or have the right to use any images you upload.
            </p>
            <p className="text-[#4a4a5e] mb-3">
              <strong>Prohibited Content:</strong> You may not upload images that are illegal, infringe on intellectual property rights, contain nudity, violence, hate speech, or violate any laws.
            </p>
            <p className="text-[#4a4a5e]">
              <strong>Content Storage:</strong> Uploaded images and generated avatars are stored temporarily and may be deleted after a reasonable period.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">5. Intellectual Property Rights</h2>
            <p className="text-[#4a4a5e] mb-3">
              <strong>Your Content:</strong> You retain all rights to images you upload.
            </p>
            <p className="text-[#4a4a5e] mb-3">
              <strong>Generated Avatars:</strong> You own the generated pixel art avatars created from your uploaded images. You may use them for personal or commercial purposes.
            </p>
            <p className="text-[#4a4a5e]">
              <strong>Service Content:</strong> All rights to the Service, including the website, software, and AI models, are owned by Mini-Aura.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">6. Service Availability</h2>
            <p className="text-[#4a4a5e]">
              We strive to provide reliable service but do not guarantee uninterrupted availability. The Service may be temporarily unavailable due to maintenance, updates, or technical issues. We reserve the right to modify or discontinue the Service at any time.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">7. Limitation of Liability</h2>
            <p className="text-[#4a4a5e] mb-3">
              The Service is provided "as is" without warranties of any kind. Mini-Aura is not liable for:
            </p>
            <ul className="list-disc list-inside text-[#4a4a5e] space-y-2 ml-4">
              <li>Loss of data or content</li>
              <li>Service interruptions or errors</li>
              <li>Quality of generated avatars</li>
              <li>Indirect, incidental, or consequential damages</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">8. Account Termination</h2>
            <p className="text-[#4a4a5e]">
              We reserve the right to suspend or terminate accounts that violate these Terms of Service, engage in fraudulent activity, or abuse the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">9. Changes to Terms</h2>
            <p className="text-[#4a4a5e]">
              We may update these Terms of Service from time to time. Continued use of the Service after changes constitutes acceptance of the updated terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">10. Contact</h2>
            <p className="text-[#4a4a5e]">
              For questions about these Terms of Service, please contact us through our website.
            </p>
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
