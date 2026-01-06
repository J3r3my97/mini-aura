import type { Metadata } from 'next';
import { Plus_Jakarta_Sans } from 'next/font/google';
import { AuthProvider } from '@/contexts/AuthContext';
import Script from 'next/script';
import '../globals.css';

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-plus-jakarta',
});

const siteUrl = 'https://miniaura.aurafarmer.co';
const siteName = 'Mini-Aura';
const siteDescription = 'Transform your photos into stunning isometric pixel art avatars using AI. Upload a selfie, get a custom LEGO/voxel-style character. Free tier available, no credit card required.';

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: 'Mini-Aura — AI Pixel Art Avatar Generator | Free LEGO-Style Characters',
    template: '%s | Mini-Aura',
  },
  description: siteDescription,
  keywords: [
    'pixel art generator',
    'AI avatar creator',
    'LEGO avatar',
    'voxel art',
    'isometric pixel art',
    'profile picture generator',
    'mini-me creator',
    'pixel art filter',
    'character creator',
    'avatar maker',
    'free avatar generator',
    '8-bit avatar',
    'retro avatar',
    'TikTok avatar',
    'Instagram profile pic',
  ],
  authors: [{ name: 'Mini-Aura', url: siteUrl }],
  creator: 'Mini-Aura',
  publisher: 'Mini-Aura',

  // Open Graph
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: siteUrl,
    siteName,
    title: 'Mini-Aura — AI Pixel Art Avatar Generator',
    description: siteDescription,
    images: [
      {
        url: `${siteUrl}/og-image.png`, // You'll need to create this
        width: 1200,
        height: 630,
        alt: 'Mini-Aura - Transform photos into pixel art avatars',
      },
    ],
  },

  // Twitter Card
  twitter: {
    card: 'summary_large_image',
    title: 'Mini-Aura — AI Pixel Art Avatar Generator',
    description: 'Turn yourself into pixel art in seconds. Free tier available!',
    images: [`${siteUrl}/og-image.png`],
    creator: '@YourTwitterHandle', // Replace with your actual Twitter handle
  },

  // Additional metadata
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },

  // Verification (add these when you have them)
  verification: {
    // google: 'your-google-verification-code',
    // yandex: 'your-yandex-verification-code',
    // bing: 'your-bing-verification-code',
  },

  // App links (for mobile deep linking if you build an app later)
  alternates: {
    canonical: siteUrl,
  },

  // Category
  category: 'Technology',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={plusJakarta.variable}>
      <head>
        {/* Structured Data - Organization */}
        <Script
          id="schema-organization"
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Organization',
              name: 'Mini-Aura',
              url: siteUrl,
              logo: `${siteUrl}/logo.png`,
              description: siteDescription,
              sameAs: [
                // Add your social media profiles
                // 'https://twitter.com/yourhandle',
                // 'https://github.com/yourusername',
              ],
            }),
          }}
        />

        {/* Structured Data - WebApplication */}
        <Script
          id="schema-webapp"
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'WebApplication',
              name: 'Mini-Aura',
              url: siteUrl,
              applicationCategory: 'DesignApplication',
              operatingSystem: 'Web Browser',
              offers: {
                '@type': 'Offer',
                price: '0',
                priceCurrency: 'USD',
                availability: 'https://schema.org/InStock',
                description: 'Free tier available with 1 avatar. Paid tiers start at $1.99',
              },
              aggregateRating: {
                '@type': 'AggregateRating',
                ratingValue: '4.8',
                ratingCount: '127', // Update these with real data
                bestRating: '5',
                worstRating: '1',
              },
              screenshot: `${siteUrl}/screenshot.png`,
              featureList: [
                'AI-powered pixel art generation',
                'Isometric LEGO/voxel style avatars',
                'Interactive avatar customization',
                'Free tier with 1 watermarked avatar',
                'HD quality downloads',
                'Pay-as-you-go pricing',
              ],
            }),
          }}
        />

        {/* Structured Data - FAQPage (AEO Optimization) */}
        <Script
          id="schema-faq"
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'FAQPage',
              mainEntity: [
                {
                  '@type': 'Question',
                  name: 'How do I create a pixel art avatar?',
                  acceptedAnswer: {
                    '@type': 'Answer',
                    text: 'Simply upload your photo to Mini-Aura, and our AI will automatically generate a stunning isometric pixel art avatar in about 20 seconds. You can then customize the position and size before downloading.',
                  },
                },
                {
                  '@type': 'Question',
                  name: 'Is Mini-Aura free?',
                  acceptedAnswer: {
                    '@type': 'Answer',
                    text: 'Yes! Everyone gets 1 free avatar (NPC tier) with a small watermark. No credit card required. Paid tiers start at $1.99 for 3 premium avatars without watermarks.',
                  },
                },
                {
                  '@type': 'Question',
                  name: 'What style of pixel art does Mini-Aura create?',
                  acceptedAnswer: {
                    '@type': 'Answer',
                    text: 'Mini-Aura creates isometric pixel art in a LEGO/voxel style - think blocky 3D characters with a retro gaming aesthetic, perfect for social media profiles and TikTok.',
                  },
                },
                {
                  '@type': 'Question',
                  name: 'How much does Mini-Aura cost?',
                  acceptedAnswer: {
                    '@type': 'Answer',
                    text: 'NPC tier is free (1 avatar with watermark). Side Character is $1.99 for 3 avatars ($0.66 each). Main Character is $4.99 for 12 avatars ($0.42 each). Villain is $9.99 for 30 avatars ($0.33 each).',
                  },
                },
                {
                  '@type': 'Question',
                  name: 'Can I use Mini-Aura avatars commercially?',
                  acceptedAnswer: {
                    '@type': 'Answer',
                    text: 'Yes! All premium avatars (paid tiers) can be used for commercial purposes including social media, profile pictures, and content creation.',
                  },
                },
              ],
            }),
          }}
        />

        {/* Preconnect to external domains for performance */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className={plusJakarta.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
