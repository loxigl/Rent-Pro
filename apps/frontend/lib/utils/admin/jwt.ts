/**
 * Утилиты для работы с JWT-токенами
 */

// Базовый URL API
import { getApiBaseUrl } from '@/lib/api/config';

/**
 * Проверяет, истек ли токен
 * @param token JWT-токен
 * @returns true если токен истек, иначе false
 */
export const isTokenExpired = (token: string): boolean => {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(window.atob(base64));

        // Получаем время истечения токена в секундах
        const exp = payload.exp;

        // Текущее время в секундах
        const now = Math.floor(Date.now() / 1000);

        // Токен истек, если текущее время больше времени истечения
        return now >= exp;
    } catch (error) {
        console.error('Error parsing token:', error);
        // В случае ошибки считаем токен истекшим
        return true;
    }
};

/**
 * Обновляет токены с использованием refresh token
 * @returns Promise<void>
 */
export const refreshTokens = async (): Promise<void> => {
    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) {
        throw new Error('Нет токена обновления');
    }

    try {
        const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                refresh_token: refreshToken,
            }),
        });

        if (!response.ok) {
            throw new Error('Ошибка обновления токена');
        }

        const data = await response.json();

        // Сохраняем новые токены
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('tokenTimestamp', Date.now().toString());

    } catch (error) {
        console.error('Error refreshing token:', error);
        // Удаляем токены при ошибке обновления
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('tokenTimestamp');
        throw error;
    }
};

/**
 * Возвращает актуальный access token
 * Если токен истек, пытается обновить его
 * @returns Promise<string> - актуальный access token
 */
export const getAccessToken = async (): Promise<string> => {
    let accessToken = localStorage.getItem('access_token');

    if (!accessToken) {
        throw new Error('No access token available');
    }

    if (isTokenExpired(accessToken)) {
        await refreshTokens();
        accessToken = localStorage.getItem('access_token');

        if (!accessToken) {
            throw new Error('Failed to get access token');
        }
    }

    return accessToken;
};

/**
 * Выходит из системы (удаляет токены)
 * @returns Promise<void>
 */
export const logout = async (): Promise<void> => {
    const refreshToken = localStorage.getItem('refresh_token');

    if (refreshToken) {
        try {
            const accessToken = await getAccessToken();

            // Отправляем запрос на логаут
            await fetch(`${getApiBaseUrl()}/api/v1/auth/logout`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({refresh_token: refreshToken}),
            });
        } catch (error) {
            console.error('Error during logout:', error);
        }
    }

    // Удаляем токены в любом случае
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('tokenTimestamp');
};

/**
 * Выполняет авторизацию администратора
 * @param username Имя пользователя
 * @param password Пароль
 * @returns Токены доступа и обновления
 */
export const loginAdmin = async (username: string, password: string) => {
    const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/admin/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username,
            password,
        }),
    });

    if (!response.ok) {
        throw new Error('Ошибка авторизации');
    }

    const data = await response.json();
    
    // Сохраняем токены в локальном хранилище
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    
    return data;
};