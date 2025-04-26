import {MetadataRoute} from 'next'
import {getApartments} from '@/lib/api/apartments'

/**
 * Динамическая генерация sitemap.xml
 * @see https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap
 */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    // Получаем все доступные квартиры
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://avitorentpro.ru'
    const response = await getApartments({page_size: 40})

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
    const apartmentPages: MetadataRoute.Sitemap = response.items.map((apartment) => ({
        url: `${baseUrl}/apartment/${apartment.id}`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.8,
    }))

    return [...staticPages, ...apartmentPages]
}