"use client";

import Image from "next/image";
import { useState, useEffect } from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination, Thumbs, Zoom } from "swiper/modules";
import { Swiper as SwiperType } from "swiper/types";
import { getOptimizedImageUrl, generateSizes } from "@/lib/utils/optimizeImage";

// Импортируем стили Swiper
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import "swiper/css/thumbs";
import "swiper/css/zoom";

interface ImageGalleryProps {
  images: string[];
  title: string;
}

/**
 * Компонент галереи изображений с миниатюрами и навигацией
 */
export default function ImageGallery({ images, title }: ImageGalleryProps) {
  const [thumbsSwiper, setThumbsSwiper] = useState<SwiperType | null>(null);
  const [imagesLoaded, setImagesLoaded] = useState<boolean[]>([]);

  // Запасное изображение, если images пустой массив
  const fallbackImage = "/images/apartment-placeholder.jpg";
  const displayImages = images.length > 0 ? images : [fallbackImage];

  // Инициализация массива загруженных изображений
  useEffect(() => {
    setImagesLoaded(new Array(displayImages.length).fill(false));
  }, [displayImages.length]);

  // Обработчик загрузки изображения
  const handleImageLoad = (index: number) => {
    setImagesLoaded(prev => {
      const newState = [...prev];
      newState[index] = true;
      return newState;
    });
  };

  return (
    <div className="apartment-gallery mb-8">
      {/* Основной слайдер */}
      <Swiper
        modules={[Navigation, Pagination, Thumbs, Zoom]}
        navigation
        pagination={{ clickable: true }}
        thumbs={{ swiper: thumbsSwiper && !thumbsSwiper.destroyed ? thumbsSwiper : null }}
        zoom={{ maxRatio: 2 }}
        className="mb-2 rounded-lg overflow-hidden"
        spaceBetween={10}
      >
        {displayImages.map((image, index) => (
          <SwiperSlide key={index}>
            <div className="relative aspect-video w-full swiper-zoom-container">
              {/* Скелетон до загрузки изображения */}
              {!imagesLoaded[index] && (
                <div className="absolute inset-0 bg-secondary-200 animate-skeleton-pulse" />
              )}

              <Image
                src={getOptimizedImageUrl(image, 'webp', 'medium')}
                alt={`${title} - Фото ${index + 1}`}
                fill
                sizes={generateSizes('gallery')}
                className="object-cover"
                priority={index === 0}
                onLoad={() => handleImageLoad(index)}
              />
            </div>
          </SwiperSlide>
        ))}
      </Swiper>

      {/* Слайдер миниатюр */}
      {displayImages.length > 1 && (
        <Swiper
          modules={[Thumbs]}
          onSwiper={setThumbsSwiper}
          spaceBetween={10}
          slidesPerView="auto"
          className="thumbs"
          watchSlidesProgress
        >
          {displayImages.map((image, index) => (
            <SwiperSlide
              key={index}
              className="w-20 h-20 rounded overflow-hidden cursor-pointer opacity-70 hover:opacity-100 transition-opacity"
            >
              <div className="relative w-full h-full">
                <Image
                  src={getOptimizedImageUrl(image, 'webp', 'thumbnail')}
                  alt={`Миниатюра ${index + 1}`}
                  fill
                  sizes={generateSizes('thumbnail')}
                  className="object-cover"
                />
              </div>
            </SwiperSlide>
          ))}
        </Swiper>
      )}
    </div>
  );
}

/**
 * Компонент скелетона для галереи изображений
 */
export function ImageGallerySkeleton() {
  return (
    <div className="apartment-gallery mb-8">
      <div className="relative aspect-video w-full rounded-lg overflow-hidden bg-secondary-200 animate-skeleton-pulse mb-2" />

      <div className="flex space-x-2 overflow-hidden">
        {Array.from({ length: 4 }).map((_, index) => (
          <div
            key={index}
            className="w-20 h-20 rounded overflow-hidden bg-secondary-200 animate-skeleton-pulse"
          />
        ))}
      </div>
    </div>
  );
}