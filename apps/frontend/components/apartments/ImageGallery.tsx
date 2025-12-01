"use client"

import type React from "react"

import Image from "next/image"
import { useState, useCallback, useEffect, useRef } from "react"
import { cn } from "@/lib/utils"
import { ChevronLeft, ChevronRight, X, ZoomIn, Expand } from "lucide-react"

interface ImageGalleryProps {
  images: string[]
  title: string
}

type ImageOrientation = "landscape" | "portrait" | "square" | "unknown"

/**
 * Современная галерея изображений с миниатюрами, зумом и полноэкранным режимом
 * Поддерживает вертикальные и горизонтальные изображения
 */
export default function ImageGallery({ images, title }: ImageGalleryProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isZoomed, setIsZoomed] = useState(false)
  const [imagesLoaded, setImagesLoaded] = useState<boolean[]>([])
  const [imageOrientations, setImageOrientations] = useState<ImageOrientation[]>([])
  const [touchStart, setTouchStart] = useState<number | null>(null)
  const [touchEnd, setTouchEnd] = useState<number | null>(null)
  const thumbnailsRef = useRef<HTMLDivElement>(null)

  // Запасное изображение
  const fallbackImage = "/modern-apartment-interior.png"
  const displayImages = images.length > 0 ? images : [fallbackImage]

  // Инициализация массивов
  useEffect(() => {
    setImagesLoaded(new Array(displayImages.length).fill(false))
    setImageOrientations(new Array(displayImages.length).fill("unknown"))
  }, [displayImages.length])

  useEffect(() => {
    displayImages.forEach((src, index) => {
      const img = new window.Image()
      img.crossOrigin = "anonymous"
      img.onload = () => {
        const ratio = img.width / img.height
        let orientation: ImageOrientation = "square"
        if (ratio > 1.2) orientation = "landscape"
        else if (ratio < 0.8) orientation = "portrait"

        setImageOrientations((prev) => {
          const newState = [...prev]
          newState[index] = orientation
          return newState
        })
      }
      img.src = src
    })
  }, [displayImages])

  // Скролл к активной миниатюре
  useEffect(() => {
    if (thumbnailsRef.current) {
      const activeThumb = thumbnailsRef.current.children[currentIndex] as HTMLElement
      if (activeThumb) {
        activeThumb.scrollIntoView({
          behavior: "smooth",
          block: "nearest",
          inline: "center",
        })
      }
    }
  }, [currentIndex])

  // Закрытие fullscreen по Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsFullscreen(false)
        setIsZoomed(false)
      }
      if (e.key === "ArrowLeft") goToPrevious()
      if (e.key === "ArrowRight") goToNext()
    }

    if (isFullscreen) {
      document.addEventListener("keydown", handleKeyDown)
      document.body.style.overflow = "hidden"
    }

    return () => {
      document.removeEventListener("keydown", handleKeyDown)
      document.body.style.overflow = ""
    }
  }, [isFullscreen])

  const handleImageLoad = (index: number) => {
    setImagesLoaded((prev) => {
      const newState = [...prev]
      newState[index] = true
      return newState
    })
  }

  const goToNext = useCallback(() => {
    setCurrentIndex((prev) => (prev + 1) % displayImages.length)
    setIsZoomed(false)
  }, [displayImages.length])

  const goToPrevious = useCallback(() => {
    setCurrentIndex((prev) => (prev - 1 + displayImages.length) % displayImages.length)
    setIsZoomed(false)
  }, [displayImages.length])

  const goToSlide = (index: number) => {
    setCurrentIndex(index)
    setIsZoomed(false)
  }

  // Touch handlers для свайпа
  const minSwipeDistance = 50

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null)
    setTouchStart(e.targetTouches[0].clientX)
  }

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX)
  }

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return
    const distance = touchStart - touchEnd
    const isLeftSwipe = distance > minSwipeDistance
    const isRightSwipe = distance < -minSwipeDistance
    if (isLeftSwipe) goToNext()
    if (isRightSwipe) goToPrevious()
  }

  const currentOrientation = imageOrientations[currentIndex]
  const isPortrait = currentOrientation === "portrait"

  return (
    <>
      <div className="w-full space-y-3">
        {/* Основное изображение */}
        <div className="relative group">
          <div
            className={cn(
              "relative w-full overflow-hidden rounded-xl bg-muted transition-all duration-300",
              // Адаптивный aspect ratio в зависимости от ориентации
              isPortrait ? "aspect-[3/4] md:aspect-[4/5] max-h-[70vh]" : "aspect-[4/3] md:aspect-[16/9]",
            )}
            onTouchStart={onTouchStart}
            onTouchMove={onTouchMove}
            onTouchEnd={onTouchEnd}
          >
            {/* Скелетон */}
            {!imagesLoaded[currentIndex] && <div className="absolute inset-0 bg-muted animate-pulse" />}

            <Image
              src={displayImages[currentIndex] || "/placeholder.svg"}
              alt={`${title} - Фото ${currentIndex + 1}`}
              fill
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
              className={cn(
                "transition-opacity duration-300",
                imagesLoaded[currentIndex] ? "opacity-100" : "opacity-0",
                // Вертикальные изображения показываем полностью, горизонтальные заполняем
                isPortrait ? "object-contain" : "object-cover",
              )}
              priority={currentIndex === 0}
              onLoad={() => handleImageLoad(currentIndex)}
            />

            {/* Навигационные стрелки - только на десктопе */}
            {displayImages.length > 1 && (
              <>
                <button
                  onClick={goToPrevious}
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-background/80 backdrop-blur-sm flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-background shadow-lg"
                  aria-label="Предыдущее фото"
                >
                  <ChevronLeft className="w-5 h-5 text-foreground" />
                </button>
                <button
                  onClick={goToNext}
                  className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-background/80 backdrop-blur-sm flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-background shadow-lg"
                  aria-label="Следующее фото"
                >
                  <ChevronRight className="w-5 h-5 text-foreground" />
                </button>
              </>
            )}

            {/* Кнопка полноэкранного режима */}
            <button
              onClick={() => setIsFullscreen(true)}
              className="absolute top-3 right-3 w-10 h-10 rounded-full bg-background/80 backdrop-blur-sm flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-background shadow-lg"
              aria-label="Открыть на весь экран"
            >
              <Expand className="w-5 h-5 text-foreground" />
            </button>

            {/* Счётчик изображений */}
            <div className="absolute bottom-3 left-3 px-3 py-1.5 rounded-full bg-background/80 backdrop-blur-sm text-sm font-medium text-foreground shadow-lg">
              {currentIndex + 1} / {displayImages.length}
            </div>
          </div>

          {/* Индикаторы для мобильных */}
          {displayImages.length > 1 && (
            <div className="flex justify-center gap-1.5 mt-3 md:hidden">
              {displayImages.map((_, index) => (
                <button
                  key={index}
                  onClick={() => goToSlide(index)}
                  className={cn(
                    "w-2 h-2 rounded-full transition-all duration-200",
                    index === currentIndex ? "bg-primary w-6" : "bg-muted-foreground/30 hover:bg-muted-foreground/50",
                  )}
                  aria-label={`Перейти к фото ${index + 1}`}
                />
              ))}
            </div>
          )}
        </div>

        {/* Миниатюры - только для десктопа */}
        {displayImages.length > 1 && (
          <div
            ref={thumbnailsRef}
            className="hidden md:flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-muted-foreground/20 scrollbar-track-transparent"
          >
            {displayImages.map((image, index) => (
              <button
                key={index}
                onClick={() => goToSlide(index)}
                className={cn(
                  "relative flex-shrink-0 rounded-lg overflow-hidden transition-all duration-200",
                  imageOrientations[index] === "portrait" ? "w-16 h-24 lg:w-18 lg:h-28" : "w-20 h-20 lg:w-24 lg:h-24",
                  index === currentIndex
                    ? "ring-2 ring-primary ring-offset-2 ring-offset-background"
                    : "opacity-60 hover:opacity-100",
                )}
                aria-label={`Миниатюра ${index + 1}`}
              >
                <Image
                  src={image || "/placeholder.svg"}
                  alt={`Миниатюра ${index + 1}`}
                  fill
                  sizes="96px"
                  className="object-cover"
                />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Полноэкранный режим */}
      {isFullscreen && (
        <div className="fixed inset-0 z-50 bg-black/95 backdrop-blur-sm flex flex-col">
          {/* Хедер */}
          <div className="flex items-center justify-between p-4 text-white">
            <span className="text-sm font-medium">
              {currentIndex + 1} / {displayImages.length}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsZoomed(!isZoomed)}
                className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                aria-label={isZoomed ? "Уменьшить" : "Увеличить"}
              >
                <ZoomIn className="w-5 h-5" />
              </button>
              <button
                onClick={() => {
                  setIsFullscreen(false)
                  setIsZoomed(false)
                }}
                className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                aria-label="Закрыть"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Изображение */}
          <div
            className="flex-1 flex items-center justify-center p-4 overflow-auto"
            onTouchStart={onTouchStart}
            onTouchMove={onTouchMove}
            onTouchEnd={onTouchEnd}
          >
            <div
              className={cn(
                "relative transition-transform duration-300",
                isZoomed ? "w-[150vw] h-[150vh] cursor-zoom-out" : "w-full h-full max-w-5xl cursor-zoom-in",
              )}
              onClick={() => setIsZoomed(!isZoomed)}
            >
              <Image
                src={displayImages[currentIndex] || "/placeholder.svg"}
                alt={`${title} - Фото ${currentIndex + 1}`}
                fill
                sizes="100vw"
                className="object-contain"
                priority
              />
            </div>
          </div>

          {/* Навигация */}
          {displayImages.length > 1 && (
            <>
              <button
                onClick={goToPrevious}
                className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors text-white"
                aria-label="Предыдущее фото"
              >
                <ChevronLeft className="w-6 h-6" />
              </button>
              <button
                onClick={goToNext}
                className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors text-white"
                aria-label="Следующее фото"
              >
                <ChevronRight className="w-6 h-6" />
              </button>
            </>
          )}

          {/* Миниатюры внизу */}
          {displayImages.length > 1 && (
            <div className="flex justify-center gap-2 p-4 overflow-x-auto">
              {displayImages.map((image, index) => (
                <button
                  key={index}
                  onClick={() => goToSlide(index)}
                  className={cn(
                    "relative flex-shrink-0 rounded-lg overflow-hidden transition-all duration-200",
                    imageOrientations[index] === "portrait" ? "w-12 h-18" : "w-16 h-16",
                    index === currentIndex ? "ring-2 ring-white" : "opacity-50 hover:opacity-100",
                  )}
                >
                  <Image
                    src={image || "/placeholder.svg"}
                    alt={`Миниатюра ${index + 1}`}
                    fill
                    sizes="64px"
                    className="object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </>
  )
}

/**
 * Компонент скелетона для галереи изображений
 */
export function ImageGallerySkeleton() {
  return (
    <div className="w-full space-y-3">
      {/* Основное изображение */}
      <div className="relative aspect-[4/3] md:aspect-[16/9] w-full rounded-xl bg-muted animate-pulse" />

      {/* Индикаторы для мобильных */}
      <div className="flex justify-center gap-1.5 md:hidden">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="w-2 h-2 rounded-full bg-muted-foreground/20" />
        ))}
      </div>

      {/* Миниатюры для десктопа */}
      <div className="hidden md:flex gap-2">
        {Array.from({ length: 5 }).map((_, index) => (
          <div key={index} className="flex-shrink-0 w-20 h-20 lg:w-24 lg:h-24 rounded-lg bg-muted animate-pulse" />
        ))}
      </div>
    </div>
  )
}
