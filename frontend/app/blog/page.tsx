'use client';

import Link from 'next/link';

const blogPosts = [
  {
    slug: 'what-is-pixel-art-avatar',
    title: 'What Is a Pixel Art Avatar? Complete Guide for 2025',
    excerpt: 'Learn what pixel art avatars are, how they\'re created, and why fashion-forward pixel avatars like Everskies style have become the hottest trend for social media.',
    date: '2025-01-06',
    readTime: '5 min read',
    category: 'Guides',
  },
  {
    slug: 'how-to-create-pixel-art-avatar-from-photo',
    title: 'How to Create a Pixel Art Avatar from Your Photo',
    excerpt: 'Step-by-step guide to transforming your selfie into a stunning fashion pixel art avatar. Create Everskies-style avatars that showcase your personal style.',
    date: '2025-01-05',
    readTime: '4 min read',
    category: 'Tutorials',
  },
  {
    slug: 'best-pixel-art-avatar-generators',
    title: 'Best Pixel Art Avatar Generators in 2025 (Free & Paid)',
    excerpt: 'Compare the top AI-powered pixel art avatar generators. Find the best tools for creating fashion-forward Everskies-style avatars from your photos.',
    date: '2025-01-04',
    readTime: '7 min read',
    category: 'Comparisons',
  },
  {
    slug: 'pixel-art-vs-ai-art-avatars',
    title: 'Pixel Art vs AI Art Avatars: Which Style Should You Choose?',
    excerpt: 'Compare fashion pixel art avatars with AI-generated portraits. Learn which style best showcases your personal aesthetic and works for your social media.',
    date: '2025-01-03',
    readTime: '6 min read',
    category: 'Guides',
  },
  {
    slug: 'fashion-avatar-guide',
    title: 'Fashion Avatars: The Ultimate Style Guide for 2025',
    excerpt: 'Complete guide to fashion avatars and Everskies-style pixel art. Learn how to create stunning fashion avatars that showcase your personal style.',
    date: '2025-01-02',
    readTime: '5 min read',
    category: 'Guides',
  },
];

export default function BlogIndex() {
  return (
    <div className="min-h-screen bg-[#e6e7f0]">
      {/* Header */}
      <header className="sticky top-0 bg-[#e6e7f0] z-50">
        <nav className="container mx-auto px-6 py-8 flex justify-between items-center max-w-7xl">
          <Link href="/" className="text-3xl font-extrabold text-[#8b7fc7] tracking-tight">
            Mini-Aura
          </Link>
          <div className="flex items-center gap-8">
            <Link href="/" className="text-[#4a4a5e] font-medium hover:text-[#8b7fc7] transition-colors">
              Home
            </Link>
            <Link href="/blog" className="text-[#8b7fc7] font-medium">
              Blog
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero */}
      <section className="py-16">
        <div className="container mx-auto px-6 max-w-4xl text-center">
          <h1 className="text-5xl md:text-6xl font-extrabold leading-tight mb-6 bg-gradient-to-br from-[#4a4a5e] to-[#8b7fc7] bg-clip-text text-transparent">
            Fashion Avatar Blog
          </h1>
          <p className="text-xl text-[#7a7a8e] max-w-2xl mx-auto">
            Tips, tutorials, and guides for creating stunning fashion pixel art avatars. Learn how to showcase your style like Everskies.
          </p>
        </div>
      </section>

      {/* Blog Posts Grid */}
      <section className="pb-20">
        <div className="container mx-auto px-6 max-w-4xl">
          <div className="space-y-8">
            {blogPosts.map((post) => (
              <Link key={post.slug} href={`/blog/${post.slug}`}>
                <article className="neu-card rounded-3xl p-8 hover:shadow-neu-convex-hover transition-all duration-300 cursor-pointer">
                  <div className="flex items-center gap-4 mb-4">
                    <span className="inline-block bg-[#8b7fc7]/10 text-[#8b7fc7] px-3 py-1 rounded-xl text-sm font-semibold">
                      {post.category}
                    </span>
                    <span className="text-[#7a7a8e] text-sm">{post.date}</span>
                    <span className="text-[#7a7a8e] text-sm">• {post.readTime}</span>
                  </div>
                  <h2 className="text-2xl font-bold mb-3 text-[#4a4a5e] hover:text-[#8b7fc7] transition-colors">
                    {post.title}
                  </h2>
                  <p className="text-[#7a7a8e] leading-relaxed">
                    {post.excerpt}
                  </p>
                </article>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-[#f0f1f7]">
        <div className="container mx-auto px-6 max-w-4xl text-center">
          <h2 className="text-3xl font-bold mb-4 text-[#4a4a5e]">
            Ready to Create Your Fashion Avatar?
          </h2>
          <p className="text-[#7a7a8e] mb-8">
            Transform your outfit into stunning pixel art in seconds. Free to try!
          </p>
          <Link href="/" className="neu-button-accent inline-block">
            Create Your Avatar Now
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-[#f0f1f7] border-t border-[#c8c9d4]">
        <div className="container mx-auto px-6 max-w-7xl">
          <div className="text-center">
            <Link href="/" className="text-2xl font-extrabold text-[#8b7fc7] tracking-tight">
              Mini-Aura
            </Link>
            <p className="text-[#7a7a8e] mt-4">&copy; 2025 Mini-Aura. All rights reserved.</p>
            <div className="flex justify-center gap-6 mt-4">
              <Link href="/privacy" className="text-[#7a7a8e] hover:text-[#8b7fc7] transition-colors">
                Privacy
              </Link>
              <Link href="/terms" className="text-[#7a7a8e] hover:text-[#8b7fc7] transition-colors">
                Terms
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
