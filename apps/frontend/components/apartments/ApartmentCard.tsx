import Link from "next/link";
import Image from "next/image";
import { ApartmentListItem } from "@/lib/api/apartments";
import { formatApartmentFeatures, formatPrice } from "@/lib/utils/format";
import { getOptimizedImageUrl, generateSizes } from "@/lib/utils/optimizeImage";

interface ApartmentCardProps {
  apartment: ApartmentListItem;
}

/**
 * Компонент карточки квартиры для отображения в каталоге
 */
export default function ApartmentCard({ apartment }: ApartmentCardProps) {
  const { id, title, price_rub, rooms, floor, area_m2, cover_url } = apartment;

  // Формирование строки характеристик (2 комн • 56 м² • 3/9 эт.)
  const features = formatApartmentFeatures(rooms, area_m2, floor);

  // Формирование цены в формате "2 500 ₽/сутки"
  const priceFormatted = `${formatPrice(price_rub)}/сутки`;

  // Запасное изображение, если cover_url отсутствует
  const fallbackImage = "/images/apartment-placeholder.jpg";

  // Получаем оптимизированный URL изображения (предпочитаем WebP и small размер для карточек)
  const optimizedImageUrl = cover_url
    ? getOptimizedImageUrl(cover_url, 'webp', 'small')
    : fallbackImage;

  // Генерируем sizes для адаптивных изображений
  const sizes = generateSizes('card');

  return (
    <Link
      href={`/apartment/${id}`}
      className="card group transition-transform hover:-translate-y-1"
    >
      <div className="relative aspect-16/9 overflow-hidden">
        <Image
          src={optimizedImageUrl}
          alt={title}
          fill
          sizes={sizes}
          className="object-cover group-hover:scale-105 transition-transform duration-300"
          priority={false}
          loading="lazy"
        />
      </div>

      <div className="p-4">
        <h3 className="text-lg font-semibold line-clamp-1 mb-2">
          {title}
        </h3>

        <p className="text-secondary-600 text-sm mb-3">
          {features}
        </p>

        <p className="text-primary-700 font-bold">
          {priceFormatted}
        </p>
      </div>
    </Link>
  );
}

/**
 * Плейсхолдер для карточки квартиры
 */
export function ApartmentCardSkeleton() {
  return (
    <div className="card">
      <div className="relative aspect-16/9 overflow-hidden bg-secondary-200 animate-skeleton-pulse" />

      <div className="p-4 space-y-3">
        <div className="h-6 w-3/4 bg-secondary-200 animate-skeleton-pulse rounded" />
        <div className="h-4 w-1/2 bg-secondary-200 animate-skeleton-pulse rounded" />
        <div className="h-5 w-1/3 bg-secondary-200 animate-skeleton-pulse rounded" />
      </div>
    </div>
  );
}