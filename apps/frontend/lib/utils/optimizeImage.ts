/**
 * Утилиты для оптимизации отображения изображений
 */

/**
 * Генерирует строку srcSet для адаптивных изображений на основе базового URL.
 * Предполагает, что бэкенд может обрабатывать параметры width и format.
 *
 * @param baseUrl Базовый URL изображения
 * @param sizes Массив размеров для srcSet
 * @param formats Форматы изображений (webp, jpeg)
 * @returns Строка srcSet для использования в компоненте Image
 */
export function generateSrcSet(
    baseUrl: string,
    sizes: number[] = [400, 800, 1200],
    formats: ('webp' | 'jpeg')[] = ['webp']
): string {
    // Проверяем, что baseUrl существует
    if (!baseUrl) return '';

    // Если URL содержит размер и формат, используем его как есть
    if (baseUrl.includes('_small_') || baseUrl.includes('_medium_') ||
        baseUrl.includes('_large_') || baseUrl.includes('_original_')) {
        return baseUrl;
    }

    // Разделяем URL на базовую часть и расширение
    const [urlBase, extension] = baseUrl.includes('.')
        ? [baseUrl.substring(0, baseUrl.lastIndexOf('.')), baseUrl.substring(baseUrl.lastIndexOf('.'))]
        : [baseUrl, ''];

    // Формируем srcSet
    const srcSetEntries: string[] = [];

    for (const format of formats) {
        for (const size of sizes) {
            // Для бэкенда с поддержкой вариантов изображений, используем стандартные размеры
            if (size <= 400) {
                srcSetEntries.push(`${urlBase.replace(/\.(jpg|jpeg|png|webp)$/, '')}_small_${format}${extension} ${size}w`);
            } else if (size <= 800) {
                srcSetEntries.push(`${urlBase.replace(/\.(jpg|jpeg|png|webp)$/, '')}_medium_${format}${extension} ${size}w`);
            } else {
                srcSetEntries.push(`${urlBase.replace(/\.(jpg|jpeg|png|webp)$/, '')}_large_${format}${extension} ${size}w`);
            }
        }
    }

    return srcSetEntries.join(', ');
}

/**
 * Выбирает наиболее оптимальный вариант изображения (размер и формат) из URL.
 * Предпочитает WebP и оптимальные размеры для различных сценариев.
 *
 * @param url Основной URL изображения
 * @param preferredFormat Предпочтительный формат ('webp' или 'jpeg')
 * @param preferredSize Предпочтительный размер ('small', 'medium', 'large', 'original')
 * @returns Оптимизированный URL изображения
 */
export function getOptimizedImageUrl(
    url: string,
    preferredFormat: 'webp' | 'jpeg' = 'webp',
    preferredSize: 'thumbnail' | 'small' | 'medium' | 'large' | 'original' = 'medium'
): string {
    // Если URL уже содержит информацию о формате и размере
    if (url.includes(`_${preferredSize}_${preferredFormat}`)) {
        return url;
    }

    // Пытаемся извлечь baseId из URL для сопоставления с другими вариантами
    const urlParts = url.split('/');
    const filename = urlParts[urlParts.length - 1];
    const baseId = filename.split('_')[0].split('.')[0];

    // Конструируем оптимизированный URL
    const optimizedUrl = url
            .replace(/\.(jpg|jpeg|png|webp)$/, '')
            .replace(/_(thumbnail|small|medium|large|original)_(webp|jpeg)/, '')
        + `_${preferredSize}_${preferredFormat}`
        + (url.endsWith('.webp') ? '.webp' : '.jpg');

    return optimizedUrl;
}

/**
 * Генерирует параметры sizes для элемента <img> на основе контекста использования.
 *
 * @param context Контекст использования изображения ('card', 'gallery', 'thumbnail')
 * @returns Строка sizes для использования в компоненте Image
 */
export function generateSizes(context: 'card' | 'gallery' | 'thumbnail'): string {
    switch (context) {
        case 'card':
            return '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw';
        case 'gallery':
            return '(max-width: 640px) 100vw, (max-width: 1024px) 90vw, 60vw';
        case 'thumbnail':
            return '80px';
        default:
            return '100vw';
    }
}