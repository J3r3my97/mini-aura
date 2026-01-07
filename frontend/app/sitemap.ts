import { MetadataRoute } from 'next';

// Blog post slugs for sitemap generation
const blogPosts = [
  { slug: 'what-is-pixel-art-avatar', date: '2025-01-06' },
  { slug: 'how-to-create-pixel-art-avatar-from-photo', date: '2025-01-05' },
  { slug: 'best-pixel-art-avatar-generators', date: '2025-01-04' },
  { slug: 'pixel-art-vs-ai-art-avatars', date: '2025-01-03' },
  { slug: 'fashion-avatar-guide', date: '2025-01-02' },
];

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://miniaura.aurafarmer.co';

  // Core pages
  const corePages: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1,
    },
    {
      url: `${baseUrl}/account`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/blog`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.9,
    },
    {
      url: `${baseUrl}/terms`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.5,
    },
    {
      url: `${baseUrl}/privacy`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.5,
    },
  ];

  // Blog post pages
  const blogPages: MetadataRoute.Sitemap = blogPosts.map((post) => ({
    url: `${baseUrl}/blog/${post.slug}`,
    lastModified: new Date(post.date),
    changeFrequency: 'monthly' as const,
    priority: 0.8,
  }));

  return [...corePages, ...blogPages];
}
