"use client";

import Link from 'next/link';
import {useState, useEffect} from 'react';

export default function AdminDashboard() {
    const [stats, setStats] = useState({
        totalApartments: 0,
        activeApartments: 0,
        totalPhotos: 0,
        totalBookings: 0,
    });
    const [isLoading, setIsLoading] = useState(true);

    // В будущем здесь будет запрос к API для получения статистики
    useEffect(() => {
        const fetchStats = async () => {
            try {
                setIsLoading(true);

                // В будущем это будет заменено на реальный API-запрос
                // const response = await fetch('/admin/api/v1/stats');
                // const data = await response.json();

                // Пока используем моковые данные
                setTimeout(() => {
                    setStats({
                        totalApartments: 12,
                        activeApartments: 8,
                        totalPhotos: 45,
                        totalBookings: 5,
                    });
                    setIsLoading(false);
                }, 500);
            } catch (error) {
                console.error('Ошибка при загрузке статистики:', error);
                setIsLoading(false);
            }
        };

        fetchStats();
    }, []);

    return (
        <div>
            <h1 className="text-2xl font-bold mb-6">Панель управления</h1>

            {/* Карточки статистики */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <StatCard
                    title="Квартиры"
                    value={stats.totalApartments}
                    description={`${stats.activeApartments} активных квартир`}
                    icon={
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 20 20"
                             fill="currentColor">
                            <path
                                d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
                        </svg>
                    }
                    isLoading={isLoading}
                    linkHref="/admin/apartments"
                    linkText="Управление квартирами"
                />

                <StatCard
                    title="Фотографии"
                    value={stats.totalPhotos}
                    description="Всего фотографий"
                    icon={
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 20 20"
                             fill="currentColor">
                            <path fillRule="evenodd"
                                  d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
                                  clipRule="evenodd"/>
                        </svg>
                    }
                    isLoading={isLoading}
                    linkHref="/admin/apartments"
                    linkText="Управление фотографиями"
                />

                <StatCard
                    title="Заявки"
                    value={stats.totalBookings}
                    description="Бронирования квартир"
                    icon={
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 20 20"
                             fill="currentColor">
                            <path
                                d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z"/>
                        </svg>
                    }
                    isLoading={isLoading}
                    linkHref="/admin/bookings"
                    linkText="Управление бронированиями"
                />
            </div>

            {/* Быстрые действия */}
            <h2 className="text-xl font-semibold mb-4">Быстрые действия</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                <QuickActionCard
                    title="Добавить квартиру"
                    description="Создать новую квартиру для сдачи"
                    icon={
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24"
                             stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                        </svg>
                    }
                    href="/admin/apartments/new"
                />

                <QuickActionCard
                    title="Управление бронированиями"
                    description="Просмотр и обработка заявок на бронирование"
                    icon={
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24"
                             stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                        </svg>
                    }
                    href="/admin/bookings"
                />

                <QuickActionCard
                    title="Журнал событий"
                    description="Просмотр журнала действий в системе"
                    icon={
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24"
                             stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                        </svg>
                    }
                    href="/admin/events"
                />
            </div>
        </div>
    );
}

// Компонент карточки статистики
interface StatCardProps {
    title: string;
    value: number | string;
    description: string;
    icon: React.ReactNode;
    isLoading: boolean;
    linkHref?: string;
    linkText?: string;
    disabled?: boolean;
}

function StatCard({title, value, description, icon, isLoading, linkHref, linkText, disabled}: StatCardProps) {
    return (
        <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-700">{title}</h3>
                <div className="text-primary-600">{icon}</div>
            </div>

            {isLoading ? (
                <div className="h-8 bg-gray-200 animate-pulse rounded-md mb-2"></div>
            ) : (
                <div className="text-3xl font-bold text-gray-900 mb-2">{value}</div>
            )}

            <p className="text-gray-500 mb-4">{description}</p>

            {linkHref && linkText && !disabled && (
                <Link href={linkHref} className="text-primary-600 hover:text-primary-700 font-medium text-sm">
                    {linkText} →
                </Link>
            )}

            {disabled && (
                <span className="text-gray-400 font-medium text-sm">
          {linkText || 'Скоро доступно'} →
        </span>
            )}
        </div>
    );
}

// Компонент карточки быстрого действия
interface QuickActionCardProps {
    title: string;
    description: string;
    icon: React.ReactNode;
    href: string;
}

function QuickActionCard({title, description, icon, href}: QuickActionCardProps) {
    return (
        <Link href={href} className="block bg-white p-4 rounded-lg shadow-sm hover:shadow transition-shadow">
            <div className="flex items-center">
                <div className="p-2 rounded-md bg-primary-50 text-primary-600 mr-4">
                    {icon}
                </div>
                <div>
                    <h3 className="font-medium text-gray-900">{title}</h3>
                    <p className="text-sm text-gray-500">{description}</p>
                </div>
            </div>
        </Link>
    );
}