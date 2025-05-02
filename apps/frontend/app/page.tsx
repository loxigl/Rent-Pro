import {Button} from "@/components/ui/button";
import Link from "next/link";
import {getApartments} from "@/lib/api/apartments";
import ApartmentCard from "@/components/apartments/ApartmentCard";
export const dynamic = 'force-dynamic';
/**
 * Главная страница с ограниченным количеством квартир и призывом перейти в каталог
 */
export default async function HomePage() {
    // Получаем только 3 квартиры для главной страницы
    const {items: featuredApartments} = await getApartments({
        page: 1,
        page_size: 3
    });

    return (
        <div>
            {/* Герой-секция */}
            <section className="bg-primary-700 text-white py-16 md:py-24">
                <div className="container-custom">
                    <div className="max-w-2xl">
                        <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
                            Аренда квартир в Невинномысске
                        </h1>
                        <p className="text-lg md:text-xl mb-8 text-primary-100">
                            Комфортное жилье для вашего отдыха или командировки.
                            Современные квартиры по доступным ценам.
                        </p>
                        <Link href="/catalog">
                            <Button size="lg" className="font-semibold px-8">
                                Смотреть каталог
                            </Button>
                        </Link>
                    </div>
                </div>
            </section>

            {/* Секция с преимуществами */}
            <section className="py-12 md:py-16 bg-white">
                <div className="container-custom">
                    <h2 className="text-center text-2xl md:text-3xl font-bold mb-12">
                        Почему выбирают нас
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="flex flex-col items-center text-center p-6">
                            <div className="bg-primary-100 p-4 rounded-full mb-4">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="24"
                                    height="24"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    className="text-primary-700"
                                >
                                    <path d="M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16"/>
                                    <path d="M1 21h22"/>
                                    <path d="M10 9h4"/>
                                    <path d="M10 13h4"/>
                                    <path d="M10 17h4"/>
                                </svg>
                            </div>
                            <h3 className="text-xl font-semibold mb-2">Удобное расположение</h3>
                            <p className="text-secondary-600">
                                Все наши квартиры находятся в центре города или рядом с ключевыми объектами
                                инфраструктуры.
                            </p>
                        </div>

                        <div className="flex flex-col items-center text-center p-6">
                            <div className="bg-primary-100 p-4 rounded-full mb-4">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="24"
                                    height="24"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    className="text-primary-700"
                                >
                                    <path
                                        d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
                                    <circle cx="12" cy="12" r="3"/>
                                </svg>
                            </div>
                            <h3 className="text-xl font-semibold mb-2">Комфорт и уют</h3>
                            <p className="text-secondary-600">
                                Наши квартиры оснащены всем необходимым для комфортного проживания,
                                включая бытовую технику и интернет.
                            </p>
                        </div>

                        <div className="flex flex-col items-center text-center p-6">
                            <div className="bg-primary-100 p-4 rounded-full mb-4">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="24"
                                    height="24"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    className="text-primary-700"
                                >
                                    <path d="M12 2v20"/>
                                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                                </svg>
                            </div>
                            <h3 className="text-xl font-semibold mb-2">Доступные цены</h3>
                            <p className="text-secondary-600">
                                Мы предлагаем конкурентные цены и специальные предложения
                                для длительного проживания.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Секция с избранными квартирами */}
            <section className="py-12 md:py-16 bg-secondary-50">
                <div className="container-custom">
                    <div className="flex justify-between items-center mb-8">
                        <h2 className="text-2xl md:text-3xl font-bold">
                            Популярные квартиры
                        </h2>

                        <Link href="/catalog">
                            <Button variant="secondary">
                                Смотреть все
                            </Button>
                        </Link>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {featuredApartments.map((apartment) => (
                            <ApartmentCard key={apartment.id} apartment={apartment}/>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA секция */}
            <section className="py-12 md:py-16 bg-primary-600 text-white">
                <div className="container-custom text-center">
                    <h2 className="text-2xl md:text-3xl font-bold mb-6">
                        Готовы забронировать квартиру?
                    </h2>
                    <p className="text-lg mb-8 max-w-2xl mx-auto text-primary-100">
                        Просмотрите наш каталог и выберите подходящий вариант для вашего пребывания в Невинномысске.
                    </p>
                    <Link href="/catalog">
                        <Button
                            size="lg"
                            className="bg-white text-primary-700 hover:bg-primary-50 font-semibold"
                        >
                            Перейти в каталог
                        </Button>
                    </Link>
                </div>
            </section>
        </div>
    );
}