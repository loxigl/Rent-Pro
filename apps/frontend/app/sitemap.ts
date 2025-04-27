import {MetadataRoute} from 'next'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://avitorentpro.ru'

    try {
        // Получаем все доступные квартиры только если API доступен
        const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/v1' || 'http://localhost:8000/api/v1'
        const response = await fetch(`${apiUrl}/apartments?page_size=40`, {
            cache: 'no-store',
            next: {revalidate: 0}
        })

        if (!response.ok) throw new Error('API недоступен')

        const data = await response.json()

        // Создаем записи для статических страниц
        const staticPages: MetadataRoute.Sitemap = [
            {
                url: `${baseUrl}/`,
                lastModified: new Date(),
                changeFrequency: 'daily',
                priority: 1.0,
            },
            {
                url: `${baseUrl}/catalog`,
                lastModified: new Date(),
                changeFrequency: 'daily',
                priority: 0.9,
            },
        ]

        // Добавляем записи для квартир
        const apartmentPages: MetadataRoute.Sitemap = data.items.map((apartment: any) => ({
            url: `${baseUrl}/apartment/${apartment.id}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.8,
        }))

        return [...staticPages, ...apartmentPages]
    } catch (error) {
        console.warn(baseUrl, '  Ошибка при получении данных для sitemap:', error)

        // Возвращаем только статические страницы в случае ошибки
        return [
            {
                url: `${baseUrl}/`,
                lastModified: new Date(),
                changeFrequency: 'daily',
                priority: 1.0,
            },
            {
                url: `${baseUrl}/catalog`,
                lastModified: new Date(),
                changeFrequency: 'daily',
                priority: 0.9,
            },
        ]
    }
}