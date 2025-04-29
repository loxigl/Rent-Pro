/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',

    images: {
        domains: ['localhost', 'minio', process.env.NEXT_PUBLIC_MINIO_HOST || ''],
        remotePatterns: [
            {
                protocol: 'http',
                hostname: '**',
            },
            {
                protocol: 'https',
                hostname: '**',
            },
        ],
    },
    // Добавляем переменные среды для сборки
    env: {
        BUILD_MODE: process.env.BUILD_MODE || 'dynamic',
        USE_LOCAL_SITEMAP_DATA: process.env.NEXT_PUBLIC_USE_LOCAL_SITEMAP_DATA || 'false'
    }
}

module.exports = nextConfig