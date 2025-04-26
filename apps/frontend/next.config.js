/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'minio', process.env.NEXT_PUBLIC_MINIO_HOST || 'localhost'],
    formats: ['image/webp'],
  },
  experimental: {
    // Включаем Server Components
    serverComponents: true,
    // Включаем ISR для страницы каталога
    isrMemoryCacheSize: 0,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;