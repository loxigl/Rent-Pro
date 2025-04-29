import {MetadataRoute} from 'next'
import fs from 'fs';
import path from 'path';

// Установлен явно период обновления для ISR
export const revalidate = 86400; // 24 часа

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://kvartiry26.ru'

    // Создаем записи для статических страниц - этот набор всегда возвращается
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
    ];

    // Проверяем, находимся ли мы в режиме статической сборки
    if (process.env.BUILD_MODE === 'static') {
        console.log('Используем только статические страницы в sitemap');
        return staticPages;
    }

    // Проверяем локальный файл данных (только если флаг USE_LOCAL_SITEMAP_DATA включен)
    if (process.env.NEXT_PUBLIC_USE_LOCAL_SITEMAP_DATA === 'true') {
        try {
            const localDataPath = path.join(process.cwd(), 'public', 'sitemap-data.json');
            console.log('Sitemap: Поиск локального файла данных:', localDataPath);

            if (fs.existsSync(localDataPath)) {
                const localDataContent = fs.readFileSync(localDataPath, 'utf8');
                const localData = JSON.parse(localDataContent);

                if (localData && localData.items && Array.isArray(localData.items)) {
                    console.log(`Sitemap: Найдено ${localData.items.length} квартир в локальном файле`);

                    const apartmentPages = localData.items.map((apartment: any) => ({
                        url: `${baseUrl}/apartment/${apartment.id}`,
                        lastModified: new Date(),
                        changeFrequency: 'weekly',
                        priority: 0.8,
                    }));

                    return [...staticPages, ...apartmentPages];
                }
            }
        } catch (error) {
            console.log('Sitemap: Ошибка при чтении локального файла данных:', error);
        }
    }

    // В остальных случаях пытаемся получить данные от API
    try {
        // Получаем все доступные квартиры только если API доступен
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
        const apiUrl = `${apiBaseUrl}/api/v1/apartments?page_size=40`;
        console.log('Sitemap: запрос к API по адресу', apiUrl);

        const response = await fetch(apiUrl, {
            next: {revalidate: 3600} // Кешируем на 1 час
        });

        if (!response.ok) {
            throw new Error(`API вернул статус ${response.status}`);
        }

        const data = await response.json();

        // Добавляем записи для квартир
        const apartmentPages: MetadataRoute.Sitemap = data.items.map((apartment: any) => ({
            url: `${baseUrl}/apartment/${apartment.id}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.8,
        }));

        return [...staticPages, ...apartmentPages];
    } catch (error) {
        console.warn('Ошибка при получении данных для sitemap:', error);

        // Возвращаем только статические страницы в случае ошибки
        return staticPages;
    }
}