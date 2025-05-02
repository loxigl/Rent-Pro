"use client";

import {useState, useEffect} from 'react';
import {useRouter} from 'next/navigation';
import {Button} from '@/components/ui/button';
import {getAccessToken} from '@/lib/utils/admin/jwt';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Определение интерфейса для данных квартиры
interface ApartmentFormData {
    title: string;
    price_rub: number;
    rooms: number;
    floor: number;
    area_m2: number;
    address: string;
    description: string;
    active: boolean;
}

// Определение интерфейса для исходных данных квартиры (при редактировании)
interface ApartmentDetail extends ApartmentFormData {
    id: number;
    photos_count: number;
    created_at: string;
    updated_at: string;
}

interface ApartmentFormProps {
    apartmentId?: number; // Если передан, то это режим редактирования
    onSuccess?: (apartment: ApartmentDetail) => void;
}

export default function ApartmentForm({apartmentId, onSuccess}: ApartmentFormProps) {
    const router = useRouter();

    // Состояния формы
    const [formData, setFormData] = useState<ApartmentFormData>({
        title: '',
        price_rub: 1500,
        rooms: 1,
        floor: 1,
        area_m2: 35,
        address: '',
        description: '',
        active: true
    });

    const [isLoading, setIsLoading] = useState(false);
    const [isFetchingData, setIsFetchingData] = useState(false);
    const [errors, setErrors] = useState<Record<string, string>>({});
    const [submitError, setSubmitError] = useState<string | null>(null);

    // Загружаем данные квартиры при редактировании
    useEffect(() => {
        if (apartmentId) {
            const fetchApartmentData = async () => {
                try {
                    setIsFetchingData(true);

                    // Получаем токен доступа
                    const token = await getAccessToken();

                    // Выполняем запрос
                    const response = await fetch(`${API_URL}/admin/api/v1/apartments/${apartmentId}`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`Ошибка загрузки данных: ${response.status}`);
                    }

                    const data: ApartmentDetail = await response.json();

                    // Устанавливаем данные формы
                    setFormData({
                        title: data.title,
                        price_rub: data.price_rub,
                        rooms: data.rooms,
                        floor: data.floor,
                        area_m2: data.area_m2,
                        address: data.address,
                        description: data.description || '',
                        active: data.active
                    });
                } catch (err: any) {
                    setSubmitError(err.message || 'Ошибка загрузки данных квартиры');
                    console.error('Ошибка при загрузке данных квартиры:', err);
                } finally {
                    setIsFetchingData(false);
                }
            };

            fetchApartmentData();
        }
    }, [apartmentId]);

    // Обработчик изменения полей формы
    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const {name, value, type} = e.target;

        // Для чекбоксов обрабатываем отдельно
        if (type === 'checkbox') {
            const checkbox = e.target as HTMLInputElement;
            setFormData({
                ...formData,
                [name]: checkbox.checked
            });
            return;
        }

        // Для числовых полей преобразуем значение
        if (type === 'number') {
            setFormData({
                ...formData,
                [name]: parseFloat(value)
            });
            return;
        }

        // Для остальных полей просто устанавливаем значение
        setFormData({
            ...formData,
            [name]: value
        });
    };

    // Валидация формы
    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        // Проверка заголовка
        if (!formData.title) {
            newErrors.title = 'Заголовок обязателен';
        } else if (formData.title.length < 20) {
            newErrors.title = 'Заголовок должен содержать не менее 20 символов';
        } else if (formData.title.length > 120) {
            newErrors.title = 'Заголовок должен содержать не более 120 символов';
        }

        // Проверка цены
        if (formData.price_rub <= 0) {
            newErrors.price_rub = 'Цена должна быть больше 0';
        } else if (formData.price_rub % 50 !== 0) {
            newErrors.price_rub = 'Цена должна быть кратна 50';
        }

        // Проверка комнат
        if (formData.rooms < 1 || formData.rooms > 6) {
            newErrors.rooms = 'Количество комнат должно быть от 1 до 6';
        }

        // Проверка этажа
        if (formData.floor < 1) {
            newErrors.floor = 'Этаж должен быть больше 0';
        }

        // Проверка площади
        if (formData.area_m2 < 10) {
            newErrors.area_m2 = 'Площадь должна быть не менее 10 м²';
        } else if (formData.area_m2 > 150) {
            newErrors.area_m2 = 'Площадь должна быть не более 150 м²';
        }

        // Проверка адреса
        if (!formData.address) {
            newErrors.address = 'Адрес обязателен';
        } else if (formData.address.length < 5) {
            newErrors.address = 'Адрес должен содержать не менее 5 символов';
        } else if (formData.address.length > 255) {
            newErrors.address = 'Адрес должен содержать не более 255 символов';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    // Обработчик отправки формы
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // Сбрасываем ошибки
        setSubmitError(null);

        // Проверяем форму
        if (!validateForm()) {
            return;
        }

        try {
            setIsLoading(true);

            // Получаем токен доступа
            const token = await getAccessToken();

            // Настраиваем URL и метод в зависимости от режима (создание/редактирование)
            const url = apartmentId
                ? `${API_URL}/admin/api/v1/apartments/${apartmentId}`
                : `${API_URL}/admin/api/v1/apartments`;

            const method = apartmentId ? 'PATCH' : 'POST';

            // Выполняем запрос
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                // Пытаемся получить детали ошибки из ответа
                const errorData = await response.json().catch(() => null);
                throw new Error(
                    errorData?.detail || `Ошибка ${method === 'POST' ? 'создания' : 'обновления'} квартиры: ${response.status}`
                );
            }

            const data: ApartmentDetail = await response.json();

            // Вызываем колбэк успешного сохранения
            if (onSuccess) {
                onSuccess(data);
            }

            // Перенаправляем на страницу редактирования или список квартир
            if (!apartmentId) {
                router.push(`/admin/apartments/${data.id}/edit`);
            } else {
                // Показываем сообщение об успешном сохранении
                alert('Квартира успешно обновлена');
            }
        } catch (err: any) {
            setSubmitError(err.message || 'Произошла ошибка при сохранении данных');
            console.error('Ошибка при сохранении квартиры:', err);
        } finally {
            setIsLoading(false);
        }
    };

    // Отображение загрузки данных
    if (apartmentId && isFetchingData) {
        return (
            <div className="bg-white shadow rounded-lg p-6">
                <div className="animate-pulse">
                    <div className="h-8 bg-gray-200 rounded mb-4"></div>
                    <div className="h-8 bg-gray-200 rounded mb-4"></div>
                    <div className="h-8 bg-gray-200 rounded mb-4"></div>
                    <div className="h-32 bg-gray-200 rounded"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="p-6">
                <h2 className="text-lg font-semibold mb-6">
                    {apartmentId ? 'Редактирование квартиры' : 'Добавление новой квартиры'}
                </h2>

                {submitError && (
                    <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-md">
                        {submitError}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    {/* Заголовок */}
                    <div className="mb-4">
                        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                            Заголовок *
                        </label>
                        <input
                            type="text"
                            id="title"
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 ${
                                errors.title ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-primary-500'
                            }`}
                            required
                        />
                        {errors.title && (
                            <p className="mt-1 text-sm text-red-600">{errors.title}</p>
                        )}
                        <p className="mt-1 text-xs text-gray-500">
                            От 20 до 120 символов. Текущая длина: {formData.title.length}
                        </p>
                    </div>

                    {/* Цена */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div>
                            <label htmlFor="price_rub" className="block text-sm font-medium text-gray-700 mb-1">
                                Цена (₽/сутки) *
                            </label>
                            <input
                                type="number"
                                id="price_rub"
                                name="price_rub"
                                value={formData.price_rub}
                                onChange={handleChange}
                                step="50"
                                min="0"
                                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 ${
                                    errors.price_rub ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-primary-500'
                                }`}
                                required
                            />
                            {errors.price_rub && (
                                <p className="mt-1 text-sm text-red-600">{errors.price_rub}</p>
                            )}
                            <p className="mt-1 text-xs text-gray-500">
                                Должна быть кратна 50
                            </p>
                        </div>

                        {/* Комнаты */}
                        <div>
                            <label htmlFor="rooms" className="block text-sm font-medium text-gray-700 mb-1">
                                Количество комнат *
                            </label>
                            <select
                                id="rooms"
                                name="rooms"
                                value={formData.rooms}
                                onChange={handleChange}
                                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 ${
                                    errors.rooms ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-primary-500'
                                }`}
                                required
                            >
                                <option value="1">1 комната</option>
                                <option value="2">2 комнаты</option>
                                <option value="3">3 комнаты</option>
                                <option value="4">4 комнаты</option>
                                <option value="5">5 комнат</option>
                                <option value="6">6 комнат</option>
                            </select>
                            {errors.rooms && (
                                <p className="mt-1 text-sm text-red-600">{errors.rooms}</p>
                            )}
                        </div>

                        {/* Этаж */}
                        <div>
                            <label htmlFor="floor" className="block text-sm font-medium text-gray-700 mb-1">
                                Этаж *
                            </label>
                            <input
                                type="number"
                                id="floor"
                                name="floor"
                                value={formData.floor}
                                onChange={handleChange}
                                min="1"
                                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 ${
                                    errors.floor ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-primary-500'
                                }`}
                                required
                            />
                            {errors.floor && (
                                <p className="mt-1 text-sm text-red-600">{errors.floor}</p>
                            )}
                        </div>
                    </div>

                    {/* Площадь */}
                    <div className="mb-4">
                        <label htmlFor="area_m2" className="block text-sm font-medium text-gray-700 mb-1">
                            Площадь (м²) *
                        </label>
                        <input
                            type="number"
                            id="area_m2"
                            name="area_m2"
                            value={formData.area_m2}
                            onChange={handleChange}
                            min="10"
                            max="150"
                            step="0.1"
                            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 ${
                                errors.area_m2 ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-primary-500'
                            }`}
                            required
                        />
                        {errors.area_m2 && (
                            <p className="mt-1 text-sm text-red-600">{errors.area_m2}</p>
                        )}
                        <p className="mt-1 text-xs text-gray-500">
                            От 10 до 150 м²
                        </p>
                    </div>

                    {/* Адрес */}
                    <div className="mb-4">
                        <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
                            Адрес *
                        </label>
                        <input
                            type="text"
                            id="address"
                            name="address"
                            value={formData.address}
                            onChange={handleChange}
                            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 ${
                                errors.address ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-primary-500'
                            }`}
                            required
                        />
                        {errors.address && (
                            <p className="mt-1 text-sm text-red-600">{errors.address}</p>
                        )}
                        <p className="mt-1 text-xs text-gray-500">
                            Полный адрес квартиры
                        </p>
                    </div>

                    {/* Описание */}
                    <div className="mb-4">
                        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                            Описание
                        </label>
                        <textarea
                            id="description"
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            rows={6}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary-500"
                        ></textarea>
                        <p className="mt-1 text-xs text-gray-500">
                            Полное описание квартиры. Поддерживается Markdown.
                        </p>
                    </div>

                    {/* Статус активности */}
                    <div className="mb-6">
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                id="active"
                                name="active"
                                checked={formData.active}
                                onChange={handleChange}
                                className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                            />
                            <label htmlFor="active" className="ml-2 block text-sm text-gray-700">
                                Активна (видна в каталоге)
                            </label>
                        </div>
                        <p className="mt-1 text-xs text-gray-500">
                            Если опция выключена, квартира будет скрыта из публичного каталога
                        </p>
                    </div>

                    {/* Кнопки действий */}
                    <div className="flex justify-end space-x-3">
                        <Button
                            type="button"
                            variant="secondary"
                            onClick={() => router.push('/admin/apartments')}
                            disabled={isLoading}
                        >
                            Отмена
                        </Button>
                        <Button
                            type="submit"
                            disabled={isLoading}
                        >
                            {isLoading ? 'Сохранение...' : apartmentId ? 'Сохранить изменения' : 'Создать квартиру'}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
}