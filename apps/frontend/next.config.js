/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',

    images: {
        domains: ['localhost', 'minio', process.env.NEXT_PUBLIC_MINIO_HOST || '', 'admin.kvartiry26.ru', 'kvartiry26.ru'],
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
    },
    // Настройка заголовков для кросс-доменных запросов
    async headers() {
        return [
            {
                source: '/:path*',
                headers: [
                    {
                        key: 'Access-Control-Allow-Origin',
                        value: '*',
                    },
                ],
            },
        ]
    }
}

module.exports = nextConfig