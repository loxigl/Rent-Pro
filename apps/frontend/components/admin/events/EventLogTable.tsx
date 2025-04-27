"use client";

import {useState, useEffect} from 'react';
import {Button} from '@/components/ui/Button';
import {getEvents, EventLogItem, EventType, EntityType} from '@/lib/api/admin/events';

interface EventLogTableProps {
    initialFilters?: {
        user_id?: number;
        event_type?: EventType;
        entity_type?: EntityType;
        start_date?: string;
        end_date?: string;
    };
}

export default function EventLogTable({initialFilters = {}}: EventLogTableProps) {
    const [events, setEvents] = useState<EventLogItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [pageSize] = useState(20);

    // Фильтры
    const [filters, setFilters] = useState({
        user_id: initialFilters.user_id,
        event_type: initialFilters.event_type,
        entity_type: initialFilters.entity_type,
        start_date: initialFilters.start_date,
        end_date: initialFilters.end_date
    });

    // Новые значения фильтров (для формы)
    const [newFilters, setNewFilters] = useState({...filters});

    // Состояние для отображения детальной информации о событии
    const [selectedEvent, setSelectedEvent] = useState<EventLogItem | null>(null);

    // Загружаем данные при изменении страницы или фильтров
    useEffect(() => {
        const fetchEventsData = async () => {
            try {
                setIsLoading(true);
                setError(null);

                // Получаем список событий с учетом фильтров
                const response = await getEvents({
                    page,
                    page_size: pageSize,
                    ...filters
                });

                setEvents(response.items);
                setTotalPages(Math.ceil(response.total / response.page_size));
            } catch (err: any) {
                setError(err.message || 'Произошла ошибка при загрузке данных');
                console.error('Ошибка при загрузке событий:', err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchEventsData();
    }, [page, pageSize, filters]);

    // Обработчик применения фильтров
    const handleApplyFilters = (e: React.FormEvent) => {
        e.preventDefault();
        setFilters({...newFilters});
        setPage(1); // Сбрасываем страницу при изменении фильтров
    };

    // Обработчик сброса фильтров
    const handleResetFilters = () => {
        setNewFilters({
            user_id: undefined,
            event_type: undefined,
            entity_type: undefined,
            start_date: undefined,
            end_date: undefined
        });
        setFilters({
            user_id: undefined,
            event_type: undefined,
            entity_type: undefined,
            start_date: undefined,
            end_date: undefined
        });
        setPage(1);
    };

    // Обработчик изменения полей фильтров
    const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
        const {name, value} = e.target;
        setNewFilters({
            ...newFilters,
            [name]: value === '' ? undefined : value
        });
    };

    // Форматирование даты и времени
    const formatDateTime = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    // Форматирование типа события для отображения
    const formatEventType = (eventType: string) => {
        const eventTypeMap: Record<string, string> = {
            'user_login': 'Вход пользователя',
            'user_logout': 'Выход пользователя',
            'apartment_created': 'Создание квартиры',
            'apartment_updated': 'Обновление квартиры',
            'apartment_deleted': 'Удаление квартиры',
            'photo_uploaded': 'Загрузка фото',
            'photo_deleted': 'Удаление фото',
            'photo_updated': 'Обновление фото'
        };

        return eventTypeMap[eventType] || eventType;
    };

    // Получение цвета для типа события
    const getEventTypeColor = (eventType: string) => {
        const eventTypeColorMap: Record<string, string> = {
            'user_login': 'bg-blue-100 text-blue-800',
            'user_logout': 'bg-blue-100 text-blue-800',
            'apartment_created': 'bg-green-100 text-green-800',
            'apartment_updated': 'bg-yellow-100 text-yellow-800',
            'apartment_deleted': 'bg-red-100 text-red-800',
            'photo_uploaded': 'bg-purple-100 text-purple-800',
            'photo_deleted': 'bg-red-100 text-red-800',
            'photo_updated': 'bg-yellow-100 text-yellow-800'
        };

        return eventTypeColorMap[eventType] || 'bg-gray-100 text-gray-800';
    };

    // Отображение загрузки
    if (isLoading && events.length === 0) {
        return (
            <div className="bg-white shadow rounded-lg p-4">
                <div className="animate-pulse">
                    <div className="h-8 bg-gray-200 rounded mb-4"></div>
                    <div className="h-64 bg-gray-200 rounded"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white shadow rounded-lg overflow-hidden">
            {/* Фильтры */}
            <div className="p-4 border-b">
                <h2 className="text-lg font-semibold mb-4">Фильтры</h2>

                <form onSubmit={handleApplyFilters} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* Тип события */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Тип события</label>
                        <select
                            name="event_type"
                            value={newFilters.event_type || ''}
                            onChange={handleFilterChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                        >
                            <option value="">Все типы</option>
                            <option value="user_login">Вход пользователя</option>
                            <option value="user_logout">Выход пользователя</option>
                            <option value="apartment_created">Создание квартиры</option>
                            <option value="apartment_updated">Обновление квартиры</option>
                            <option value="apartment_deleted">Удаление квартиры</option>
                            <option value="photo_uploaded">Загрузка фото</option>
                            <option value="photo_deleted">Удаление фото</option>
                            <option value="photo_updated">Обновление фото</option>
                        </select>
                    </div>

                    {/* Тип сущности */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Тип сущности</label>
                        <select
                            name="entity_type"
                            value={newFilters.entity_type || ''}
                            onChange={handleFilterChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                        >
                            <option value="">Все сущности</option>
                            <option value="apartment">Квартира</option>
                            <option value="photo">Фотография</option>
                            <option value="user">Пользователь</option>
                        </select>
                    </div>

                    {/* Дата начала */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Дата начала</label>
                        <input
                            type="date"
                            name="start_date"
                            value={newFilters.start_date || ''}
                            onChange={handleFilterChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                        />
                    </div>

                    {/* Дата окончания */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Дата окончания</label>
                        <input
                            type="date"
                            name="end_date"
                            value={newFilters.end_date || ''}
                            onChange={handleFilterChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                        />
                    </div>

                    {/* Кнопки действий */}
                    <div className="flex space-x-3 items-end lg:col-start-3">
                        <Button
                            type="button"
                            variant="secondary"
                            onClick={handleResetFilters}
                        >
                            Сбросить
                        </Button>
                        <Button type="submit">
                            Применить
                        </Button>
                    </div>
                </form>
            </div>

            {/* Сообщение об ошибке */}
            {error && (
                <div className="p-4 border-b">
                    <div className="bg-red-50 text-red-700 p-3 rounded-md">
                        {error}
                    </div>
                </div>
            )}

            {/* Таблица событий */}
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                    <tr>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Дата и время
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Тип события
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Пользователь
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Сущность
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Действия
                        </th>
                    </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                    {events.length > 0 ? (
                        events.map((event) => (
                            <tr key={event.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {formatDateTime(event.timestamp)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                    <span
                        className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getEventTypeColor(event.event_type)}`}>
                      {formatEventType(event.event_type)}
                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {event.user_email || `ID: ${event.user_id || 'N/A'}`}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {event.entity_type ? (
                                        <>
                                            <span className="font-medium">{event.entity_type}</span>
                                            {event.entity_id && (
                                                <span className="ml-1">#{event.entity_id}</span>
                                            )}
                                        </>
                                    ) : (
                                        'N/A'
                                    )}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button
                                        onClick={() => setSelectedEvent(event)}
                                        className="text-primary-600 hover:text-primary-900"
                                    >
                                        Детали
                                    </button>
                                </td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">
                                Нет событий, соответствующих фильтрам
                            </td>
                        </tr>
                    )}
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

            {/* Модальное окно с деталями события */}
            {selectedEvent && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                        <div className="p-6">
                            <div className="flex justify-between items-start mb-4">
                                <h3 className="text-lg font-medium">
                                    Детали события: {formatEventType(selectedEvent.event_type)}
                                </h3>
                                <button
                                    onClick={() => setSelectedEvent(null)}
                                    className="text-gray-400 hover:text-gray-500"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none"
                                         viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                              d="M6 18L18 6M6 6l12 12"/>
                                    </svg>
                                </button>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <p className="text-sm font-medium text-gray-500">ID события</p>
                                    <p className="text-sm text-gray-900">{selectedEvent.id}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-500">Дата и время</p>
                                    <p className="text-sm text-gray-900">{formatDateTime(selectedEvent.timestamp)}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-500">Тип события</p>
                                    <p className="text-sm text-gray-900">{formatEventType(selectedEvent.event_type)}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-500">Пользователь</p>
                                    <p className="text-sm text-gray-900">{selectedEvent.user_email || `ID: ${selectedEvent.user_id || 'N/A'}`}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-500">Тип сущности</p>
                                    <p className="text-sm text-gray-900">{selectedEvent.entity_type || 'N/A'}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-500">ID сущности</p>
                                    <p className="text-sm text-gray-900">{selectedEvent.entity_id || 'N/A'}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-500">IP-адрес</p>
                                    <p className="text-sm text-gray-900">{selectedEvent.ip_address || 'N/A'}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-500">User-Agent</p>
                                    <p className="text-sm text-gray-900 truncate">{selectedEvent.user_agent || 'N/A'}</p>
                                </div>
                            </div>

                            {selectedEvent.payload && (
                                <div>
                                    <p className="text-sm font-medium text-gray-500 mb-1">Данные события</p>
                                    <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto">
                    {JSON.stringify(selectedEvent.payload, null, 2)}
                  </pre>
                                </div>
                            )}

                            <div className="mt-4 text-right">
                                <Button
                                    variant="secondary"
                                    size="sm"
                                    onClick={() => setSelectedEvent(null)}
                                >
                                    Закрыть
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}