"use client";

import {useState, useEffect} from 'react';
import Link from 'next/link';
import Image from 'next/image';
import {Button} from '@/components/ui/button';
import {getAccessToken} from '@/lib/utils/admin/jwt';
import {getApiBaseUrl} from '@/lib/api/config';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';

export const API_URL = getApiBaseUrl();

// Интерфейс для квартиры в списке
interface ApartmentItem {
    id: number;
    title: string;
    price_rub: number;
    rooms: number;
    area_m2: number;
    active: boolean;
    booking_enabled: boolean;
    photos_count: number;
    cover_url: string | null;
    created_at: string;
}

// Интерфейс для ответа с пагинацией
interface ApartmentListResponse {
    items: ApartmentItem[];
    total: number;
    page: number;
    page_size: number;
}

interface ApartmentTableProps {
    onApartmentDelete?: (id: number) => void;
}

export default function ApartmentTable({onApartmentDelete}: ApartmentTableProps) {
    const [apartments, setApartments] = useState<ApartmentItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [searchQuery, setSearchQuery] = useState('');
    const { toast } = useToast();

    // Загружаем данные при изменении страницы или поискового запроса
    useEffect(() => {
        const fetchApartments = async () => {
            try {
                setIsLoading(true);
                setError(null);

                // Получаем токен доступа
                const token = await getAccessToken();

                // Формируем URL с параметрами
                const url = new URL(`${API_URL}/admin/api/v1/apartments`, window.location.origin);
                url.searchParams.append('page', page.toString());
                url.searchParams.append('page_size', '10');

                if (searchQuery) {
                    url.searchParams.append('search', searchQuery);
                }

                // Выполняем запрос
                const response = await fetch(url.toString(), {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    throw new Error(`Ошибка загрузки данных: ${response.status}`);
                }

                const data: ApartmentListResponse = await response.json();

                setApartments(data.items);
                setTotalPages(Math.ceil(data.total / data.page_size));
            } catch (err: any) {
                setError(err.message || 'Произошла ошибка при загрузке данных');
                console.error('Ошибка при загрузке квартир:', err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchApartments();
    }, [page, searchQuery]);

    // Форматирование даты
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU');
    };

    // Форматирование цены
    const formatPrice = (price: number) => {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            maximumFractionDigits: 0
        }).format(price);
    };

    // Обработчик удаления квартиры
    const handleDelete = async (id: number) => {
        if (!window.confirm('Вы уверены, что хотите удалить эту квартиру?')) {
            return;
        }

        try {
            // Получаем токен доступа
            const token = await getAccessToken();

            // Выполняем запрос на удаление
            const response = await fetch(`${API_URL}/admin/api/v1/apartments/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Ошибка удаления: ${response.status}`);
            }

            // Обновляем список квартир
            setApartments(apartments.filter(apartment => apartment.id !== id));

            // Вызываем колбэк, если он передан
            if (onApartmentDelete) {
                onApartmentDelete(id);
            }
            
            toast({
                title: 'Успех',
                description: `Квартира #${id} успешно удалена`,
            });
        } catch (err: any) {
            setError(err.message || 'Произошла ошибка при удалении квартиры');
            console.error('Ошибка при удалении квартиры:', err);
            toast({
                title: 'Ошибка',
                description: 'Не удалось удалить квартиру',
                variant: 'error',
            });
        }
    };
    
    // Обработчик изменения статуса бронирования квартиры
    const handleBookingToggle = async (id: number, currentStatus: boolean) => {
        try {
            // Получаем токен доступа
            const token = await getAccessToken();
            
            // Выполняем запрос на обновление статуса бронирования
            const response = await fetch(`${API_URL}/admin/api/v1/apartments/${id}/booking-toggle?enable=${!currentStatus}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`Ошибка обновления: ${response.status}`);
            }
            
            // Обновляем статус в локальном состоянии
            setApartments(apartments.map(apartment => 
                apartment.id === id 
                    ? { ...apartment, booking_enabled: !currentStatus } 
                    : apartment
            ));
            
            toast({
                title: 'Статус бронирования обновлен',
                description: `Бронирование для квартиры теперь ${!currentStatus ? 'разрешено' : 'запрещено'}`,
            });
        } catch (err: any) {
            setError(err.message || 'Произошла ошибка при обновлении статуса бронирования');
            console.error('Ошибка при обновлении статуса бронирования:', err);
            toast({
                title: 'Ошибка',
                description: 'Не удалось обновить статус бронирования',
                variant: 'error',
            });
        }
    };

    // Отображение загрузки
    if (isLoading && apartments.length === 0) {
        return (
            <div className="bg-white shadow rounded-lg p-4">
                <div className="animate-pulse">
                    <div className="h-8 bg-gray-200 rounded mb-4"></div>
                    <div className="h-64 bg-gray-200 rounded"></div>
                </div>
            </div>
        );
    }

    // Отображение ошибки
    if (error && apartments.length === 0) {
        return (
            <div className="bg-white shadow rounded-lg p-4">
                <div className="text-red-500 mb-4">{error}</div>
                <Button onClick={() => setPage(1)}>Повторить загрузку</Button>
            </div>
        );
    }

    return (
        <div className="bg-white shadow rounded-lg overflow-hidden">
            {/* Поиск и фильтры */}
            <div className="p-4 border-b">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center">
                    <h2 className="text-lg font-semibold mb-4 sm:mb-0">Список квартир</h2>

                    <div className="flex flex-col sm:flex-row gap-2">
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="Поиск по названию..."
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                            <div className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none"
                                     viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                                </svg>
                            </div>
                        </div>

                        <div className="flex space-x-2">
                            <Link href="/admin/apartments/new">
                                <Button>
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                        fill="currentColor">
                                        <path fillRule="evenodd"
                                            d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                                            clipRule="evenodd"/>
                                    </svg>
                                    Добавить
                                </Button>
                            </Link>
                            
                            <Link href="/admin/bookings">
                                <Button variant="outline">
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                        fill="currentColor">
                                        <path fillRule="evenodd"
                                            d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
                                            clipRule="evenodd"/>
                                    </svg>
                                    Бронирования
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </div>

            {/* Мобильная версия таблицы (карточки) */}
            <div className="md:hidden">
                {apartments.map((apartment) => (
                    <div key={apartment.id} className="border-b p-4">
                        <div className="flex items-start mb-3">
                            <div className="flex-shrink-0 h-16 w-16 relative mr-3">
                                {apartment.cover_url ? (
                                    <Image
                                        src={apartment.cover_url}
                                        alt={apartment.title}
                                        className="h-16 w-16 rounded-md object-cover"
                                        width={64}
                                        height={64}
                                    />
                                ) : (
                                    <div className="h-16 w-16 rounded-md bg-gray-200 flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg"
                                            className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24"
                                            stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                                        </svg>
                                    </div>
                                )}
                                <div className="absolute -top-1 -right-1 bg-gray-100 rounded-full px-1 text-xs">
                                    {apartment.photos_count}
                                </div>
                            </div>
                            <div className="flex-1">
                                <div className="font-medium text-gray-900 line-clamp-2">
                                    {apartment.title}
                                </div>
                                <div className="text-sm text-gray-500">
                                    ID: {apartment.id}
                                </div>
                            </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-2 mb-3">
                            <div>
                                <div className="text-xs text-gray-500">Цена</div>
                                <div className="font-medium">{formatPrice(apartment.price_rub)}</div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-500">Параметры</div>
                                <div className="text-sm">{apartment.rooms} комн. • {apartment.area_m2} м²</div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-500">Дата</div>
                                <div className="text-sm">{formatDate(apartment.created_at)}</div>
                            </div>
                            <div className="flex items-center">
                                <div className="flex items-center space-x-2">
                                    <Switch 
                                        id={`booking-switch-${apartment.id}`}
                                        checked={apartment.booking_enabled}
                                        onCheckedChange={() => handleBookingToggle(apartment.id, apartment.booking_enabled)}
                                    />
                                    <Label htmlFor={`booking-switch-${apartment.id}`} className="text-xs">
                                        {apartment.booking_enabled ? 'Бронирование разрешено' : 'Бронирование запрещено'}
                                    </Label>
                                </div>
                            </div>
                        </div>
                        
                        <div className="flex justify-between">
                            <Link href={`/admin/apartments/${apartment.id}/edit`}>
                                <Button variant="outline" size="sm">Редактировать</Button>
                            </Link>
                            <Button 
                                variant="outline" 
                                size="sm" 
                                className="text-red-600 border-red-200 hover:border-red-600"
                                onClick={() => handleDelete(apartment.id)}
                            >
                                Удалить
                            </Button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Десктопная версия таблицы */}
            <div className="hidden md:block overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                    <tr>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Квартира
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Цена
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Параметры
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Статус
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Дата
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Действия
                        </th>
                    </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                    {apartments.map((apartment) => (
                        <tr key={apartment.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0 h-10 w-10 relative">
                                        {apartment.cover_url ? (
                                            <Image
                                                src={apartment.cover_url}
                                                alt={apartment.title}
                                                className="h-10 w-10 rounded-md object-cover"
                                                width={40}
                                                height={40}
                                            />
                                        ) : (
                                            <div
                                                className="h-10 w-10 rounded-md bg-gray-200 flex items-center justify-center">
                                                <svg xmlns="http://www.w3.org/2000/svg"
                                                     className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24"
                                                     stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                                          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                                                </svg>
                                            </div>
                                        )}
                                        <div className="absolute -top-1 -right-1 bg-gray-100 rounded-full px-1 text-xs">
                                            {apartment.photos_count}
                                        </div>
                                    </div>
                                    <div className="ml-4">
                                        <div className="text-sm font-medium text-gray-900 line-clamp-1">
                                            {apartment.title}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                            ID: {apartment.id}
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div
                                    className="text-sm text-gray-900 font-medium">{formatPrice(apartment.price_rub)}</div>
                                <div className="text-xs text-gray-500">/ сутки</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm text-gray-900">{apartment.rooms} комн.</div>
                                <div className="text-sm text-gray-500">{apartment.area_m2} м²</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center space-x-2">
                                    <Switch 
                                        id={`booking-switch-desk-${apartment.id}`}
                                        checked={apartment.booking_enabled}
                                        onCheckedChange={() => handleBookingToggle(apartment.id, apartment.booking_enabled)}
                                    />
                                    <Label htmlFor={`booking-switch-desk-${apartment.id}`}>
                                        {apartment.booking_enabled ? 'Бронирование разрешено' : 'Бронирование запрещено'}
                                    </Label>
                                </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {formatDate(apartment.created_at)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <div className="flex justify-end space-x-2">
                                    <Link href={`/admin/apartments/${apartment.id}/edit`}
                                          className="text-primary-600 hover:text-primary-900">
                                        Редактировать
                                    </Link>
                                    <button
                                        onClick={() => handleDelete(apartment.id)}
                                        className="text-red-600 hover:text-red-900"
                                    >
                                        Удалить
                                    </button>
                                </div>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>

            {/* Пагинация */}
            <div className="px-6 py-4 flex items-center justify-between border-t">
                <div className="text-sm text-gray-500">
                    Страница {page} из {totalPages}
                </div>
                <div className="flex space-x-2">
                    <Button
                        variant="secondary"
                        size="sm"
                        disabled={page <= 1}
                        onClick={() => setPage(page - 1)}
                    >
                        Назад
                    </Button>
                    <Button
                        variant="secondary"
                        size="sm"
                        disabled={page >= totalPages}
                        onClick={() => setPage(page + 1)}
                    >
                        Вперед
                    </Button>
                </div>
            </div>
        </div>
    );
}