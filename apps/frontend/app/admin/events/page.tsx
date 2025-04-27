"use client";

import {useState, useEffect} from 'react';
import EventLogTable from '@/components/admin/events/EventLogTable';
import {getEventStats} from '@/lib/api/admin/events';

export default function EventsPage() {
    const [stats, setStats] = useState<Record<string, number>>({});
    const [isLoadingStats, setIsLoadingStats] = useState(true);
    const [statsError, setStatsError] = useState<string | null>(null);

    // Загружаем статистику при монтировании компонента
    useEffect(() => {
        const fetchStats = async () => {
            try {
                setIsLoadingStats(true);
                setStatsError(null);

                // Получаем статистику за последний месяц
                const lastMonth = new Date();
                lastMonth.setMonth(lastMonth.getMonth() - 1);

                const stats = await getEventStats(
                    lastMonth.toISOString().split('T')[0],
                    new Date().toISOString().split('T')[0]
                );

                setStats(stats);
            } catch (err: any) {
                setStatsError(err.message || 'Произошла ошибка при загрузке статистики');
                console.error('Ошибка при загрузке статистики событий:', err);
            } finally {
                setIsLoadingStats(false);
            }
        };

        fetchStats();
    }, []);

    // Форматирование типа события для отображения в статистике
    const formatStatEventType = (eventType: string) => {
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

    return (
        <div>
            <h1 className="text-2xl font-bold mb-6">Журнал событий</h1>

            {/* Статистика событий */}
            <div className="mb-8">
                <h2 className="text-lg font-semibold mb-4">Статистика за последний месяц</h2>

                {isLoadingStats ? (
                    <div className="bg-white shadow rounded-lg p-4">
                        <div className="animate-pulse">
                            <div className="h-8 bg-gray-200 rounded mb-4"></div>
                            <div className="h-32 bg-gray-200 rounded"></div>
                        </div>
                    </div>
                ) : statsError ? (
                    <div className="bg-white shadow rounded-lg p-4">
                        <div className="text-red-500 mb-4">{statsError}</div>
                    </div>
                ) : (
                    <div className="bg-white shadow rounded-lg overflow-hidden">
                        <div className="p-4">
                            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                                {Object.entries(stats).length > 0 ? (
                                    Object.entries(stats).map(([eventType, count]) => (
                                        <div key={eventType} className="bg-gray-50 p-4 rounded-lg">
                                            <p className="text-sm text-gray-500">{formatStatEventType(eventType)}</p>
                                            <p className="text-2xl font-bold">{count}</p>
                                        </div>
                                    ))
                                ) : (
                                    <div className="col-span-4 text-center p-4">
                                        <p className="text-gray-500">Нет данных о событиях за последний месяц</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Таблица журнала событий */}
            <EventLogTable/>
        </div>
    );
}