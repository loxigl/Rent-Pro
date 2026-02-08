import {Metadata} from "next";
import {notFound} from "next/navigation";
import {getApartmentById} from "@/lib/api/apartments";
import ApartmentDetail from "./ApartmentDetail";

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
                title: `${apartment.title} | Квартиры26`,
                description: apartment.description
                    ? apartment.description.slice(0, 160).replace(/<\/?[^>]+(>|$)/g, "")
                    : `Квартира с ${apartment.rooms} комнатами, площадью ${apartment.area_m2} м²`,
                images: apartment.photos.length > 0
                    ? [{url: apartment.photos[0], alt: apartment.title}]
                    : [],
                type: "article",
            },
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
            <>
                {/* JSONSchema для SEO */}
                <script
                    type="application/ld+json"
                    dangerouslySetInnerHTML={{__html: JSON.stringify(jsonLd)}}
                />
                
                <ApartmentDetail apartment={apartment} />
            </>
        );
    } catch (error) {
        notFound(); // Используем Next.js стандартную страницу 404
    }
}