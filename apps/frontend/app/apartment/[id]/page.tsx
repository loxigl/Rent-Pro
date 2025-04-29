import {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {getApartmentById} from "@/lib/api/apartments";
import ImageGallery, {ImageGallerySkeleton} from "@/components/apartments/ImageGallery";
import ApartmentFeatures from "@/components/apartments/ApartmentFeatures";
import ContactButtons from "@/components/apartments/ContactButtons";
import {Markdown} from "@/components/ui/Markdown";
import {formatPrice} from "@/lib/utils/format";
import {Suspense} from "react";
export const revalidate=100; // Период обновления кеша (в секундах) для динамических страниц
export const dynamic = 'force-dynamic';

// Генерация метаданных для страницы
export async function generateMetadata({
                                           params
                                       }: {
    params: { id: string }
}): Promise<Metadata> {
    try {
        const id = Number(params.id);
        const apartment = await getApartmentById(id);

        return {
            title: apartment.title,
            description: apartment.description
                ? apartment.description.slice(0, 160).replace(/<\/?[^>]+(>|$)/g, "")
                : `Квартира с ${apartment.rooms} комнатами, площадью ${apartment.area_m2} м²`,
            openGraph: {
                title: `${apartment.title} | Kvartiry26`,
                description: apartment.description
                    ? apartment.description.slice(0, 160).replace(/<\/?[^>]+(>|$)/g, "")
                    : `Квартира с ${apartment.rooms} комнатами, площадью ${apartment.area_m2} м²`,
                images: apartment.photos.length > 0
                    ? [{url: apartment.photos[0], alt: apartment.title}]
                    : [],
                type: "article",
            },
            // JSON-LD для Product/Offer, поисковиков
            alternates: {
                canonical: `https://kvartiry26.ru/apartment/${id}`,
            },
        };
    } catch (error) {
        return {
            title: "Квартира не найдена",
            description: "Запрашиваемая квартира не найдена на нашем сервисе.",
        };
    }
}

/**
 * Страница детальной информации о квартире
 */
export default async function ApartmentDetailPage({
                                                      params
                                                  }: {
    params: { id: string }
}) {
    const id = Number(params.id);

    try {
        const apartment = await getApartmentById(id);

        // JSONSchema для Product (для SEO)
        const jsonLd = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": apartment.title,
            "description": apartment.description,
            "image": apartment.photos[0] || "",
            "offers": {
                "@type": "Offer",
                "price": apartment.price_rub,
                "priceCurrency": "RUB",
                "availability": "https://schema.org/InStock",
            },
        };

        return (
            <div className="py-8 md:py-12">
                <div className="container-custom">
                    {/* JSONSchema для SEO */}
                    <script
                        type="application/ld+json"
                        dangerouslySetInnerHTML={{__html: JSON.stringify(jsonLd)}}
                    />

                    {/* Хлебные крошки */}
                    <div className="mb-6">
                        <div className="flex items-center text-sm">
                            <Link href="/" className="text-secondary-500 hover:text-primary-600">
                                Главная
                            </Link>
                            <span className="mx-2 text-secondary-400">/</span>
                            <Link href="/catalog" className="text-secondary-500 hover:text-primary-600">
                                Каталог
                            </Link>
                            <span className="mx-2 text-secondary-400">/</span>
                            <span className="text-secondary-700 truncate max-w-[200px]">
                {apartment.title}
              </span>
                        </div>
                    </div>

                    {/* Заголовок */}
                    <div className="mb-6">
                        <h1 className="text-2xl md:text-3xl font-bold mb-2">
                            {apartment.title}
                        </h1>
                        <p className="text-secondary-600">
                            {apartment.address}
                        </p>
                    </div>

                    {/* Галерея изображений */}
                    <Suspense fallback={<ImageGallerySkeleton/>}>
                        <ImageGallery
                            images={apartment.photos}
                            title={apartment.title}
                        />
                    </Suspense>

                    {/* Цена и кнопки */}
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
                        <div className="text-2xl md:text-3xl font-bold text-primary-700 mb-4 md:mb-0">
                            {formatPrice(apartment.price_rub)}<span className="text-lg font-normal">/сутки</span>
                        </div>

                        <ContactButtons
                            phone="+79991234567"
                            telegram="Kvartiry26_bot"
                        />
                    </div>

                    {/* Характеристики */}
                    <ApartmentFeatures
                        rooms={apartment.rooms}
                        area_m2={apartment.area_m2}
                        floor={apartment.floor}
                        address={apartment.address}
                    />

                    {/* Описание */}
                    <div className="mt-8">
                        <h2 className="text-xl font-semibold mb-4">Описание</h2>
                        {apartment.description ? (
                            <Markdown content={apartment.description}/>
                        ) : (
                            <p className="text-secondary-600">
                                Подробное описание отсутствует.
                            </p>
                        )}
                    </div>

                    {/* Похожие квартиры (здесь будет добавлен компонент в будущем) */}
                </div>
            </div>
        );
    } catch (error) {
        notFound(); // Используем Next.js стандартную страницу 404
    }
}