'use client';

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { useAuth } from '@/contexts/AuthContext';
import SignInModal from '@/components/auth/SignInModal';
import SignUpModal from '@/components/auth/SignUpModal';
import AvatarEditor from '@/components/AvatarEditor';
import api, { JobResponse } from '@/lib/api';
import { compressImage, validateImageFile } from '@/lib/imageCompression';

export default function Home() {
  const { user, loading: authLoading, logout } = useAuth();
  const [showSignIn, setShowSignIn] = useState(false);
  const [showSignUp, setShowSignUp] = useState(false);

  // Upload state
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [currentJob, setCurrentJob] = useState<JobResponse | null>(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Customized image state
  const [customizedImage, setCustomizedImage] = useState<string | null>(null);

  const handleFileUpload = async (file: File) => {
    if (!file || !file.type.startsWith('image/')) {
      setError('Please upload a valid image file');
      return;
    }

    // Check if user is authenticated
    if (!user) {
      setShowSignIn(true);
      return;
    }

    // Validate file
    const validation = validateImageFile(file);
    if (!validation.valid) {
      setError(validation.error || 'Invalid file');
      return;
    }

    setError('');
    setUploading(true);
    setProcessing(true);

    try {
      // Compress image before upload
      const compressedFile = await compressImage(file, {
        maxWidth: 2048,
        maxHeight: 2048,
        maxSizeMB: 5,
        quality: 0.9,
      });

      // Upload and generate
      const response = await api.generateAvatar(compressedFile);
      console.log('Generation started:', response);

      // Start polling for status
      const finalJob = await api.pollJobStatus(
        response.job_id,
        (job) => {
          console.log('Job update:', job);
          setCurrentJob(job);
        },
        60, // max 60 attempts
        2000 // poll every 2 seconds
      );

      setCurrentJob(finalJob);
      setProcessing(false);
    } catch (err: any) {
      console.error('Upload failed:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to generate avatar');
      setProcessing(false);
    } finally {
      setUploading(false);
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

  const handleReset = () => {
    setCurrentJob(null);
    setProcessing(false);
    setError('');
  };

  const handleDownload = async (imageUrl?: string) => {
    const urlToDownload = imageUrl || customizedImage || currentJob?.output_image_url;
    if (!urlToDownload) return;

    try {
      const response = await fetch(urlToDownload);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mini-aura-${currentJob?.job_id || 'customized'}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  return (
    <div className="min-h-screen bg-[#e6e7f0]">
      {/* Header */}
      <header className="sticky top-0 bg-[#e6e7f0] z-50">
        <nav className="container mx-auto px-6 py-8 flex justify-between items-center max-w-7xl">
          <a href="#" className="text-3xl font-extrabold text-[#8b7fc7] tracking-tight">
            Mini-Aura
          </a>
          <div className="flex items-center gap-8">
            <a href="#features" className="text-[#4a4a5e] font-medium hover:text-[#8b7fc7] transition-colors hidden md:block">
              Features
            </a>
            <a href="#pricing" className="text-[#4a4a5e] font-medium hover:text-[#8b7fc7] transition-colors hidden md:block">
              Pricing
            </a>
            {authLoading ? (
              <div className="w-24 h-10 bg-[#e6e7f0] rounded-2xl animate-pulse"></div>
            ) : user ? (
              <div className="flex items-center gap-4">
                <span className="text-[#4a4a5e] font-medium hidden sm:block">{user.email}</span>
                <button onClick={logout} className="neu-button">
                  Sign Out
                </button>
              </div>
            ) : (
              <button onClick={() => setShowSignIn(true)} className="neu-button-accent">
                Sign In
              </button>
            )}
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="py-20 pb-32">
        <div className="container mx-auto px-6 text-center max-w-7xl">
          <h1 className="text-7xl md:text-7xl font-extrabold leading-tight mb-6 bg-gradient-to-br from-[#4a4a5e] to-[#8b7fc7] bg-clip-text text-transparent animate-float">
            Turn Yourself
            <br />
            Into Pixel Art
          </h1>
          <p className="text-2xl text-[#7a7a8e] mb-12 max-w-2xl mx-auto">
            Transform your photos into stunning pixel art avatars in seconds. One click, endless possibilities.
          </p>

          {/* Error Message */}
          {error && (
            <div className="max-w-xl mx-auto mb-8 bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-2xl">
              {error}
            </div>
          )}

          {/* Upload Zone */}
          {!processing && !currentJob && (
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
              {!user && (
                <p className="text-sm text-[#8b7fc7] mt-4 font-semibold">
                  Sign in required to generate avatars
                </p>
              )}
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
              <p className="text-[#7a7a8e] mt-4 text-lg">
                {currentJob?.status === 'queued' && 'Queued for processing...'}
                {currentJob?.status === 'processing' && 'Creating your pixel art avatar...'}
                {!currentJob && 'Uploading...'}
              </p>
              {currentJob?.status === 'processing' && (
                <p className="text-[#7a7a8e] text-sm mt-2">This usually takes 5-10 seconds</p>
              )}
            </div>
          )}

          {/* Interactive Avatar Editor */}
          {currentJob?.status === 'completed' && currentJob.metadata?.avatar_url && currentJob.input_image_url && (
            <div className="mt-12">
              <h3 className="text-2xl font-bold mb-6 text-center bg-gradient-to-br from-[#4a4a5e] to-[#8b7fc7] bg-clip-text text-transparent">
                🎮 Game Mode: Customize Your Avatar!
              </h3>
              <p className="text-[#7a7a8e] text-center mb-6 text-lg">
                Use the <span className="font-bold text-[#8b7fc7]">GBA controller</span> below or your keyboard to position your pixel avatar!
              </p>

              {/* Inline Editor */}
              <AvatarEditor
                originalImageUrl={currentJob.input_image_url}
                avatarImageUrl={currentJob.metadata.avatar_url}
                onSave={(blob) => {
                  const url = URL.createObjectURL(blob);
                  setCustomizedImage(url);
                  handleDownload(url);
                }}
                onCancel={handleReset}
              />

              {currentJob.metadata?.processing_time && (
                <p className="text-[#7a7a8e] text-sm mt-6 text-center">
                  Generated in {(currentJob.metadata.processing_time / 1000).toFixed(1)}s
                </p>
              )}
            </div>
          )}

          {/* Failed State */}
          {currentJob?.status === 'failed' && (
            <div className="mt-12">
              <div className="max-w-xl mx-auto bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-2xl mb-6">
                <p className="font-semibold mb-2">Generation Failed</p>
                <p className="text-sm">{currentJob.error_message || 'Unknown error occurred'}</p>
              </div>
              <button onClick={handleReset} className="neu-button-accent">
                Try Again
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="container mx-auto px-6 max-w-7xl">
          <h2 className="section-title">Why Everyone Loves Mini-Me</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[#8b7fc7]">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6v6l4 2" />
                </svg>
              }
              title="Instant Results"
              description="Get your pixel art avatar in under 10 seconds. No waiting, no complexity."
            />
            <FeatureCard
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[#8b7fc7]">
                  <path d="M12 2L2 7l10 5 10-5-10-5z" />
                  <path d="M2 17l10 5 10-5M2 12l10 5 10-5" />
                </svg>
              }
              title="AI-Powered Magic"
              description="Advanced AI creates stunning pixel art that captures your unique features."
            />
            <FeatureCard
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[#8b7fc7]">
                  <rect x="3" y="3" width="18" height="18" rx="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <path d="M21 15l-5-5L5 21" />
                </svg>
              }
              title="Viral-Ready"
              description="Share directly to TikTok, Instagram, Twitter. Perfect for social media."
            />
          </div>
        </div>
      </section>


      {/* Pricing Section */}
      <section id="pricing" className="py-20">
        <div className="container mx-auto px-6 max-w-7xl">
          <h2 className="section-title">Simple Pay-As-You-Go Pricing</h2>

          {/* Free tier banner */}
          <div className="max-w-3xl mx-auto mb-12 neu-card rounded-3xl p-8 text-center bg-gradient-to-br from-[#7bc89d]/10 to-[#8b7fc7]/10">
            <div className="text-4xl mb-4">🎉</div>
            <h3 className="text-2xl font-bold mb-2 text-[#4a4a5e]">
              Everyone Gets 1 Free Avatar!
            </h3>
            <p className="text-[#7a7a8e]">
              Try it out for free (with watermark). No credit card required. Just sign up and start creating!
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {pricingPlans.map((plan, idx) => (
              <PricingCard key={idx} {...plan} user={user} setShowSignIn={setShowSignIn} setError={setError} />
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
            <p className="text-[#7a7a8e]">&copy; 2025 Mini-Aura. All rights reserved. Built with AI magic.</p>
          </div>
        </div>
      </footer>

      {/* Auth Modals */}
      <SignInModal
        isOpen={showSignIn}
        onClose={() => setShowSignIn(false)}
        onSwitchToSignUp={() => {
          setShowSignIn(false);
          setShowSignUp(true);
        }}
      />
      <SignUpModal
        isOpen={showSignUp}
        onClose={() => setShowSignUp(false)}
        onSwitchToSignIn={() => {
          setShowSignUp(false);
          setShowSignIn(true);
        }}
      />

    </div>
  );
}

// Components
function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="neu-card rounded-3xl p-10 text-center">
      <div className="feature-icon mx-auto mb-6">{icon}</div>
      <h3 className="text-2xl font-bold mb-3">{title}</h3>
      <p className="text-[#7a7a8e]">{description}</p>
    </div>
  );
}

function PricingCard({ name, price, package: packageId, credits, features, featured, badge, user, setShowSignIn, setError }: any) {
  const [loading, setLoading] = useState(false);

  const handleGetStarted = async () => {
    // Require authentication
    if (!user) {
      setShowSignIn(true);
      return;
    }

    try {
      setLoading(true);

      // Create checkout session with credit package
      const session = await api.createCheckoutSession(packageId);

      // Redirect to Stripe checkout
      window.location.href = session.url;

    } catch (error: any) {
      console.error('Checkout error:', error);
      setError(error.response?.data?.detail || 'Failed to start checkout');
    } finally {
      setLoading(false);
    }
  };

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
      </div>
      <ul className="space-y-3 my-8 text-left">
        {features.map((feature: string, idx: number) => (
          <li key={idx} className="flex items-center gap-3 text-[#7a7a8e]">
            <span className="text-[#7bc89d] font-bold text-lg">✓</span>
            {feature}
          </li>
        ))}
      </ul>
      <button
        onClick={handleGetStarted}
        disabled={loading}
        className={featured ? 'neu-button-accent w-full' : 'neu-button w-full'}
      >
        {loading ? 'Loading...' : 'Purchase Credits'}
      </button>
    </div>
  );
}

// Data
const pricingPlans = [
  { name: '1 Avatar', price: '$2.99', credits: 1, package: '1_credit', features: ['1 avatar credit', 'No watermark', 'HD quality', 'Perfect for trying it out'] },
  { name: '5 Avatars', price: '$12.99', credits: 5, package: '5_credits', features: ['5 avatar credits', 'No watermarks', 'HD quality', 'Save $2 ($2.60/avatar)', 'Great for friends'], featured: true, badge: 'Great Value' },
  { name: '10 Avatars', price: '$19.99', credits: 10, package: '10_credits', features: ['10 avatar credits', 'No watermarks', 'HD quality', 'Save $10 ($2.00/avatar)', 'Best for groups'], featured: true, badge: 'BEST VALUE' },
];

const footerSections = [
  { title: 'Product', links: [{ text: 'Features', href: '#features' }, { text: 'Pricing', href: '#pricing' }, { text: 'API', href: '#' }, { text: 'Roadmap', href: '#' }] },
  { title: 'Company', links: [{ text: 'About', href: '#' }, { text: 'Blog', href: '#' }, { text: 'Careers', href: '#' }, { text: 'Press Kit', href: '#' }] },
  { title: 'Resources', links: [{ text: 'Documentation', href: '#' }, { text: 'Tutorials', href: '#' }, { text: 'Support', href: '#' }, { text: 'Status', href: '#' }] },
  { title: 'Legal', links: [{ text: 'Privacy', href: '/privacy' }, { text: 'Terms', href: '/terms' }, { text: 'License', href: '#' }, { text: 'Cookie Policy', href: '#' }] },
];
