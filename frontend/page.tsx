'use client';

import { useState, useRef } from 'react';
import Image from 'next/image';

export default function Home() {
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    if (!file || !file.type.startsWith('image/')) {
      alert('Please upload a valid image file');
      return;
    }

    setUploading(true);
    setProcessing(true);

    const formData = new FormData();
    formData.append('image', file);

    try {
      // Call your API endpoint
      const response = await fetch('/api/generate', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.image_url) {
        setResultUrl(data.image_url);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to generate avatar. Please try again.');
    } finally {
      setUploading(false);
      setProcessing(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  return (
    <div className="min-h-screen bg-[#e6e7f0]">
      {/* Header */}
      <header className="sticky top-0 bg-[#e6e7f0] z-50">
        <nav className="container mx-auto px-6 py-8 flex justify-between items-center max-w-7xl">
          <a href="#" className="text-3xl font-extrabold text-[#8b7fc7] tracking-tight">
            Mini-Me
          </a>
          <div className="flex items-center gap-8">
            <a href="#features" className="text-[#4a4a5e] font-medium hover:text-[#8b7fc7] transition-colors">
              Features
            </a>
            <a href="#examples" className="text-[#4a4a5e] font-medium hover:text-[#8b7fc7] transition-colors">
              Examples
            </a>
            <a href="#pricing" className="text-[#4a4a5e] font-medium hover:text-[#8b7fc7] transition-colors">
              Pricing
            </a>
            <button className="neu-button-accent">Sign In</button>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="py-20 pb-32">
        <div className="container mx-auto px-6 text-center max-w-7xl">
          <h1 className="text-7xl font-extrabold leading-tight mb-6 bg-gradient-to-br from-[#4a4a5e] to-[#8b7fc7] bg-clip-text text-transparent animate-float">
            Turn Yourself
            <br />
            Into Pixel Art
          </h1>
          <p className="text-2xl text-[#7a7a8e] mb-12 max-w-2xl mx-auto">
            Transform your photos into stunning pixel art avatars in seconds. One click, endless possibilities.
          </p>

          {/* Upload Zone */}
          {!processing && !resultUrl && (
            <div
              className={`upload-zone ${isDragging ? 'dragging' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="upload-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-10 h-10 text-[#8b7fc7]"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-3">Drop your photo here</h3>
              <p className="text-[#7a7a8e]">or click to browse • JPG, PNG up to 10MB</p>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                className="hidden"
              />
            </div>
          )}

          {/* Processing State */}
          {processing && (
            <div className="mt-12">
              <div className="loader mx-auto"></div>
              <p className="text-[#7a7a8e] mt-4">Creating your pixel art avatar...</p>
            </div>
          )}

          {/* Result Preview */}
          {resultUrl && (
            <div className="mt-12">
              <div className="result-image mx-auto max-w-md">
                <Image
                  src={resultUrl}
                  alt="Your pixel art avatar"
                  width={400}
                  height={400}
                  className="rounded-3xl"
                />
              </div>
              <div className="flex gap-4 justify-center mt-8 flex-wrap">
                <button className="neu-button-accent">Download</button>
                <button className="neu-button">Share</button>
                <button
                  className="neu-button"
                  onClick={() => {
                    setResultUrl(null);
                    setProcessing(false);
                  }}
                >
                  Create Another
                </button>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="container mx-auto px-6 max-w-7xl">
          <h2 className="section-title">Why Everyone Loves Mini-Me</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, idx) => (
              <FeatureCard key={idx} {...feature} />
            ))}
          </div>
        </div>
      </section>

      {/* Gallery Section */}
      <section id="examples" className="py-20 bg-[#f0f1f7]">
        <div className="container mx-auto px-6 max-w-7xl">
          <h2 className="section-title">Real Transformations</h2>
          <div className="grid md:grid-cols-4 gap-8 mt-12">
            {galleryImages.map((img, idx) => (
              <div key={idx} className="neu-card aspect-square rounded-3xl overflow-hidden">
                <Image
                  src={img.url}
                  alt={img.alt}
                  width={600}
                  height={600}
                  className="w-full h-full object-cover"
                />
              </div>
            ))}
          </div>
          <p className="text-center mt-8 text-[#7a7a8e]">
            Note: These are example portraits. Generated pixel art results will be shown after upload.
          </p>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20">
        <div className="container mx-auto px-6 max-w-7xl">
          <h2 className="section-title">Simple Pricing</h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {pricingPlans.map((plan, idx) => (
              <PricingCard key={idx} {...plan} />
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 bg-[#f0f1f7]">
        <div className="container mx-auto px-6 max-w-7xl">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            {footerSections.map((section, idx) => (
              <div key={idx}>
                <h4 className="text-lg font-bold mb-4">{section.title}</h4>
                <ul className="space-y-2">
                  {section.links.map((link, linkIdx) => (
                    <li key={linkIdx}>
                      <a href={link.href} className="text-[#7a7a8e] hover:text-[#8b7fc7] transition-colors">
                        {link.text}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="text-center pt-8 border-t border-[#c8c9d4]">
            <p className="text-[#7a7a8e]">&copy; 2025 Mini-Me. All rights reserved. Built with AI magic.</p>
          </div>
        </div>
      </footer>

      <style jsx>{`
        .neu-button {
          background: #e6e7f0;
          border: none;
          border-radius: 16px;
          padding: 16px 32px;
          font-weight: 600;
          font-size: 16px;
          color: #4a4a5e;
          box-shadow: 8px 8px 16px #c8c9d4, -8px -8px 16px #ffffff;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .neu-button:hover {
          box-shadow: 4px 4px 8px #c8c9d4, -4px -4px 8px #ffffff;
        }

        .neu-button:active {
          box-shadow: inset 4px 4px 8px #c8c9d4, inset -4px -4px 8px #ffffff;
          transform: scale(0.98);
        }

        .neu-button-accent {
          background: linear-gradient(135deg, #8b7fc7, #6b5eb0);
          color: white;
          border: none;
          border-radius: 16px;
          padding: 16px 32px;
          font-weight: 600;
          font-size: 16px;
          box-shadow: 6px 6px 12px rgba(139, 127, 199, 0.3), -6px -6px 12px rgba(255, 255, 255, 0.5);
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .neu-button-accent:hover {
          box-shadow: 8px 8px 16px rgba(139, 127, 199, 0.4), -8px -8px 16px rgba(255, 255, 255, 0.6);
        }

        .neu-card {
          background: #e6e7f0;
          box-shadow: 8px 8px 16px #c8c9d4, -8px -8px 16px #ffffff;
          transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        .neu-card:hover {
          box-shadow: 12px 12px 24px #c8c9d4, -12px -12px 24px #ffffff;
          transform: translateY(-4px);
        }

        .upload-zone {
          background: #e6e7f0;
          border-radius: 32px;
          box-shadow: inset 6px 6px 12px #c8c9d4, inset -6px -6px 12px #ffffff;
          padding: 80px 40px;
          max-width: 600px;
          margin: 48px auto;
          cursor: pointer;
          transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
          position: relative;
        }

        .upload-zone:hover {
          transform: scale(1.02);
        }

        .upload-zone.dragging {
          box-shadow: inset 4px 4px 8px #c8c9d4, inset -4px -4px 8px #ffffff;
          transform: scale(0.98);
        }

        .upload-icon {
          width: 80px;
          height: 80px;
          margin: 0 auto 24px;
          background: #e6e7f0;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 8px 8px 16px #c8c9d4, -8px -8px 16px #ffffff;
        }

        .section-title {
          font-size: 48px;
          font-weight: 800;
          text-align: center;
          margin-bottom: 64px;
          color: #4a4a5e;
        }

        .loader {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: conic-gradient(from 0deg, #8b7fc7, #6b5eb0, #8b7fc7);
          animation: spin 1.5s linear infinite;
          position: relative;
        }

        .loader::after {
          content: '';
          position: absolute;
          inset: 8px;
          background: #e6e7f0;
          border-radius: 50%;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

        @keyframes float {
          0%,
          100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        .animate-float {
          animation: float 3s ease-in-out infinite;
        }

        @media (max-width: 768px) {
          h1 {
            font-size: 48px !important;
          }
          .section-title {
            font-size: 36px;
          }
        }
      `}</style>
    </div>
  );
}

// Feature Card Component
function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="neu-card rounded-3xl p-10 text-center">
      <div className="feature-icon mx-auto mb-6">{icon}</div>
      <h3 className="text-2xl font-bold mb-3">{title}</h3>
      <p className="text-[#7a7a8e]">{description}</p>
    </div>
  );
}

// Pricing Card Component
function PricingCard({
  name,
  price,
  period,
  features,
  featured,
  badge,
}: {
  name: string;
  price: string;
  period: string;
  features: string[];
  featured?: boolean;
  badge?: string;
}) {
  return (
    <div className={`neu-card rounded-3xl p-12 text-center ${featured ? 'bg-gradient-to-br from-[#8b7fc7]/10 to-[#6b5eb0]/10' : ''}`}>
      {badge && (
        <div className="inline-block bg-[#8b7fc7] text-white px-4 py-1.5 rounded-xl text-xs font-bold uppercase mb-4">
          {badge}
        </div>
      )}
      <h3 className="text-3xl font-extrabold mb-4">{name}</h3>
      <div className="mb-2">
        <span className="text-6xl font-extrabold text-[#8b7fc7]">{price}</span>
        <span className="text-xl text-[#7a7a8e] font-medium">/{period}</span>
      </div>
      <ul className="space-y-3 my-8 text-left">
        {features.map((feature, idx) => (
          <li key={idx} className="flex items-center gap-3 text-[#7a7a8e]">
            <span className="text-[#7bc89d] font-bold text-lg">✓</span>
            {feature}
          </li>
        ))}
      </ul>
      <button className={featured ? 'neu-button-accent w-full' : 'neu-button w-full'}>
        {featured ? 'Start Free Trial' : 'Get Started'}
      </button>
    </div>
  );
}

// Data
const features = [
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[#8b7fc7]">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 6v6l4 2" />
      </svg>
    ),
    title: 'Instant Results',
    description: 'Get your pixel art avatar in under 10 seconds. No waiting, no complexity.',
  },
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[#8b7fc7]">
        <path d="M12 2L2 7l10 5 10-5-10-5z" />
        <path d="M2 17l10 5 10-5M2 12l10 5 10-5" />
      </svg>
    ),
    title: 'AI-Powered Magic',
    description: 'Advanced AI creates stunning pixel art that captures your unique features.',
  },
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[#8b7fc7]">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <path d="M21 15l-5-5L5 21" />
      </svg>
    ),
    title: 'Viral-Ready',
    description: 'Share directly to TikTok, Instagram, Twitter. Perfect for social media.',
  },
];

const galleryImages = [
  { url: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=600&q=80', alt: 'Portrait transformation example' },
  { url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&q=80', alt: 'Portrait transformation example' },
  { url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&q=80', alt: 'Portrait transformation example' },
  { url: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=600&q=80', alt: 'Portrait transformation example' },
];

const pricingPlans = [
  {
    name: 'Free',
    price: '$0',
    period: 'month',
    features: ['3 avatars per month', 'Standard quality', 'Watermark included', 'Basic support'],
  },
  {
    name: 'Pro',
    price: '$9',
    period: 'month',
    features: ['Unlimited avatars', 'HD quality exports', 'No watermarks', 'Priority processing', 'Commercial license'],
    featured: true,
    badge: 'Most Popular',
  },
  {
    name: 'One-Time',
    price: '$3',
    period: 'avatar',
    features: ['Single HD avatar', 'No subscription', 'No watermark', 'Personal use only'],
  },
];

const footerSections = [
  {
    title: 'Product',
    links: [
      { text: 'Features', href: '#features' },
      { text: 'Pricing', href: '#pricing' },
      { text: 'API', href: '#' },
      { text: 'Roadmap', href: '#' },
    ],
  },
  {
    title: 'Company',
    links: [
      { text: 'About', href: '#' },
      { text: 'Blog', href: '#' },
      { text: 'Careers', href: '#' },
      { text: 'Press Kit', href: '#' },
    ],
  },
  {
    title: 'Resources',
    links: [
      { text: 'Documentation', href: '#' },
      { text: 'Tutorials', href: '#' },
      { text: 'Support', href: '#' },
      { text: 'Status', href: '#' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { text: 'Privacy', href: '#' },
      { text: 'Terms', href: '#' },
      { text: 'License', href: '#' },
      { text: 'Cookie Policy', href: '#' },
    ],
  },
];
