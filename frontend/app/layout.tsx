import type { Metadata } from 'next';
import { Plus_Jakarta_Sans } from 'next/font/google';
import { AuthProvider } from '@/contexts/AuthContext';
import '../globals.css';

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-plus-jakarta',
});

export const metadata: Metadata = {
  title: 'Mini-Aura — AI Pixel Art Avatar Generator',
  description: 'Transform your photos into stunning pixel art avatars in seconds. One click, endless possibilities.',
  keywords: ['pixel art', 'avatar generator', 'AI', 'image generation', 'profile picture'],
  authors: [{ name: 'Mini-Aura' }],
  openGraph: {
    title: 'Mini-Aura — AI Pixel Art Avatar Generator',
    description: 'Transform your photos into stunning pixel art avatars',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={plusJakarta.variable}>
      <body className={plusJakarta.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
