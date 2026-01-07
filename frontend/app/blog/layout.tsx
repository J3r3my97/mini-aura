import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: {
    template: '%s | Mini-Aura Blog',
    default: 'Blog | Mini-Aura - Pixel Art Avatar Tips & Tutorials',
  },
  description: 'Learn about pixel art avatars, AI image generation, and creative tips for making stunning profile pictures. Expert guides from Mini-Aura.',
};

export default function BlogLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
