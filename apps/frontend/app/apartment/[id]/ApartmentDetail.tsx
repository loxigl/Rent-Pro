'use client';

import Link from "next/link";
import {Suspense} from "react";
import ImageGallery, {ImageGallerySkeleton} from "@/components/apartments/ImageGallery";
import ApartmentFeatures from "@/components/apartments/ApartmentFeatures";
import ContactButtons from "@/components/apartments/ContactButtons";
import BookingButton from "@/components/booking/BookingButton";
import {Markdown} from "@/components/ui/Markdown";
import {formatPrice} from "@/lib/utils/format";

interface ApartmentDetailProps {
    apartment: any; // Тип можно уточнить в соответствии с вашей моделью данных
}

export default function ApartmentDetail({ apartment }: ApartmentDetailProps) {
    return (
        <div className="py-8 md:py-12">
            <div className="container-custom">
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

                    <div className="flex flex-col md:flex-row gap-3">
                        <BookingButton
                            apartmentId={apartment.id}
                            price={apartment.price_rub}
                            bookingEnabled={apartment.booking_enabled}
                        />
                        <ContactButtons
                            phone="+79283209083"
                            telegram="Kvartiry26_bot"
                        />
                    </div>
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

                {/* Информация о бронировании */}
                {!apartment.booking_enabled && (
                    <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-md">
                        <h3 className="text-lg font-semibold text-amber-700 mb-2">Обратите внимание</h3>
                        <p className="text-amber-700">
                            В данный момент онлайн-бронирование для этой квартиры недоступно. 
                            Пожалуйста, свяжитесь с нами по телефону или через Telegram для получения 
                            информации о возможности аренды.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
} 