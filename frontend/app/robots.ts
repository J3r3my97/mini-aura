import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  const baseUrl = 'https://miniaura.aurafarmer.co';

  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/account/*'], // Protect account pages and API routes
      },
      {
        userAgent: 'GPTBot', // ChatGPT crawler
        allow: '/',
      },
      {
        userAgent: 'CCBot', // Common Crawl (used by many AI systems)
        allow: '/',
      },
      {
        userAgent: 'anthropic-ai', // Claude crawler
        allow: '/',
      },
      {
        userAgent: 'Google-Extended', // Google's AI training crawler
        allow: '/', // Allow for Gemini to learn about your product
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
