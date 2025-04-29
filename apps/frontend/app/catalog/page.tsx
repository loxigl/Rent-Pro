import {Metadata} from "next";
import Link from "next/link";
import {getApartments} from "@/lib/api/apartments";
import ApartmentCard, {ApartmentCardSkeleton} from "@/components/apartments/ApartmentCard";
import {Button} from "@/components/ui/Button";
import {Suspense} from "react";
export const dynamic = 'force-dynamic';

// Метаданные для страницы каталога
export const metadata: Metadata = {
    title: "Каталог квартир",
    description: "Выбирайте из множества вариантов аренды квартир в Невинномысске. Различные районы, площади и цены.",
    openGraph: {
        title: "Каталог квартир | Kvartiry26",
        description: "Выбирайте из множества вариантов аренды квартир в Невинномысске. Различные районы, площади и цены.",
    },
};

// Таймаут для Incremental Static Regeneration (ISR)
export const revalidate = 10;

// Интерфейс для параметров страницы (query-параметры)
interface CatalogPageProps {
    searchParams: {
        page?: string;
        sort?: string;
        order?: string;
    };
}

/**
 * Компонент для отображения каталога квартир
 */
export default async function CatalogPage({searchParams}: CatalogPageProps) {
    // Парсим параметры из URL
    const page = Number(searchParams.page) || 1;
    const sort = searchParams.sort === "price_rub" ? "price_rub" : "created_at";
    const order = searchParams.order === "asc" ? "asc" : "desc";

    // Получаем данные о квартирах
    const {items: apartments, total, page_size} = await getApartments({
        page,
        sort,
        order,
    });

    // Вычисляем количество страниц для пагинации
    const totalPages = Math.ceil(total / page_size);

    return (
        <div className="py-8 md:py-12">
            <div className="container-custom">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
                    <div>
                        <h1 className="text-2xl md:text-3xl font-bold mb-2">Каталог квартир</h1>
                        <p className="text-secondary-600">
                            Найдено {total} вариантов аренды в Невинномысске
                        </p>
                    </div>

                    {/* Сортировка */}
                    <div className="mt-4 md:mt-0 flex flex-wrap gap-2">
                        <Link
                            href={`/catalog?sort=created_at&order=desc${page > 1 ? `&page=${page}` : ''}`}
                            className={`px-3 py-1 rounded-md text-sm ${
                                sort === "created_at" && order === "desc"
                                    ? "bg-primary-100 text-primary-700 font-medium"
                                    : "bg-white text-secondary-700 hover:bg-secondary-50"
                            }`}
                        >
                            Новые
                        </Link>

                        <Link
                            href={`/catalog?sort=price_rub&order=asc${page > 1 ? `&page=${page}` : ''}`}
                            className={`px-3 py-1 rounded-md text-sm ${
                                sort === "price_rub" && order === "asc"
                                    ? "bg-primary-100 text-primary-700 font-medium"
                                    : "bg-white text-secondary-700 hover:bg-secondary-50"
                            }`}
                        >
                            Сначала дешевые
                        </Link>

                        <Link
                            href={`/catalog?sort=price_rub&order=desc${page > 1 ? `&page=${page}` : ''}`}
                            className={`px-3 py-1 rounded-md text-sm ${
                                sort === "price_rub" && order === "desc"
                                    ? "bg-primary-100 text-primary-700 font-medium"
                                    : "bg-white text-secondary-700 hover:bg-secondary-50"
                            }`}
                        >
                            Сначала дорогие
                        </Link>
                    </div>
                </div>

                {/* Сетка квартир с плейсхолдерами */}
                <Suspense fallback={<SkeletonGrid/>}>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {apartments.map((apartment) => (
                            <ApartmentCard key={apartment.id} apartment={apartment}/>
                        ))}
                    </div>

                    {/* Если квартир нет */}
                    {apartments.length === 0 && (
                        <div className="text-center py-12">
                            <h2 className="text-xl font-semibold mb-4">Квартиры не найдены</h2>
                            <p className="text-secondary-600 mb-6">
                                По вашему запросу не найдено ни одной квартиры.
                            </p>
                            <Link href="/catalog">
                                <Button>Сбросить фильтры</Button>
                            </Link>
                        </div>
                    )}
                </Suspense>

                {/* Пагинация */}
                {totalPages > 1 && (
                    <div className="mt-10 flex justify-center">
                        <div className="flex space-x-2">
                            {/* Кнопка "Назад" */}
                            {page > 1 && (
                                <Link
                                    href={`/catalog?page=${page - 1}&sort=${sort}&order=${order}`}
                                    className="px-4 py-2 rounded-md bg-white text-secondary-700 hover:bg-secondary-50"
                                >
                                    Назад
                                </Link>
                            )}

                            {/* Номера страниц */}
                            {Array.from({length: totalPages}, (_, i) => i + 1)
                                .filter(p => Math.abs(p - page) < 3 || p === 1 || p === totalPages)
                                .map((p, i, arr) => {
                                    // Добавляем многоточие, если нужно
                                    if (i > 0 && p - arr[i - 1] > 1) {
                                        return (
                                            <span
                                                key={`ellipsis-${p}`}
                                                className="px-4 py-2 text-secondary-400"
                                            >
                        ...
                      </span>
                                        );
                                    }

                                    return (
                                        <Link
                                            key={p}
                                            href={`/catalog?page=${p}&sort=${sort}&order=${order}`}
                                            className={`px-4 py-2 rounded-md ${
                                                p === page
                                                    ? "bg-primary-600 text-white font-medium"
                                                    : "bg-white text-secondary-700 hover:bg-secondary-50"
                                            }`}
                                        >
                                            {p}
                                        </Link>
                                    );
                                })}

                            {/* Кнопка "Далее" */}
                            {page < totalPages && (
                                <Link
                                    href={`/catalog?page=${page + 1}&sort=${sort}&order=${order}`}
                                    className="px-4 py-2 rounded-md bg-white text-secondary-700 hover:bg-secondary-50"
                                >
                                    Далее
                                </Link>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

/**
 * Компонент для отображения скелетона сетки квартир
 */
function SkeletonGrid() {
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({length: 12}).map((_, index) => (
                <ApartmentCardSkeleton key={index}/>
            ))}
        </div>
    );
}