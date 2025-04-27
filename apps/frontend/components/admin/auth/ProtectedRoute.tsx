"use client";

import {useEffect, useState, ReactNode} from 'react';
import {useRouter, usePathname} from 'next/navigation';
import {isTokenExpired, refreshTokens} from '@/lib/utils/admin/jwt';

interface ProtectedRouteProps {
    children: ReactNode;
}

/**
 * Компонент для защиты админ-маршрутов. Проверяет наличие токена и его актуальность.
 * При необходимости обновляет токен или перенаправляет на страницу логина.
 */
const ProtectedRoute = ({children}: ProtectedRouteProps) => {
    const router = useRouter();
    const pathname = usePathname();
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Игнорируем страницу логина
        if (pathname === '/admin/login') {
            setIsLoading(false);
            return;
        }

        const checkAuth = async () => {
            try {
                // Получаем токены из localStorage
                const accessToken = localStorage.getItem('accessToken');
                const refreshToken = localStorage.getItem('refreshToken');

                // Если токенов нет, перенаправляем на страницу логина
                if (!accessToken || !refreshToken) {
                    throw new Error('No tokens found');
                }

                // Проверяем, истек ли токен
                if (isTokenExpired(accessToken)) {
                    // Пытаемся обновить токен
                    await refreshTokens();
                }

                // Если все проверки пройдены, считаем пользователя аутентифицированным
                setIsAuthenticated(true);
            } catch (error) {
                console.error('Authentication error:', error);
                // Перенаправляем на страницу логина
                router.push('/admin/login');
            } finally {
                setIsLoading(false);
            }
        };

        checkAuth();
    }, [pathname, router]);

    // Показываем загрузчик, пока проверяем аутентификацию
    if (isLoading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
            </div>
        );
    }

    // Если это страница логина или пользователь аутентифицирован, показываем содержимое
    if (pathname === '/admin/login' || isAuthenticated) {
        return <>{children}</>;
    }

    // По умолчанию ничего не показываем (должны перенаправиться на логин)
    return null;
};

export default ProtectedRoute;