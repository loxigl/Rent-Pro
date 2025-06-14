/**
 * Утилиты для работы с JWT-токенами
 */

// Базовый URL API
import { getApiUrl } from '@/lib/api/config';
import { adminRoutes } from '@/lib/api/routes';

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
        return true; // В случае ошибки считаем, что токен истек
    }
};

/**
 * Сохраняет токены JWT в localStorage
 * @param accessToken Токен доступа
 * @param refreshToken Токен обновления
 */
export const setTokens = (accessToken: string, refreshToken: string): void => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
};

/**
 * Получает токен доступа из localStorage
 * @returns Токен доступа или null, если токен не найден или истек
 */
export const getAccessToken = (): string | null => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        return null;
    }

    // Если токен истек, пытаемся его обновить
    if (isTokenExpired(token)) {
        // Если у нас нет возможности обновить токен (мы не в браузере),
        // просто возвращаем null
        if (typeof window === 'undefined') {
            return null;
        }
        
        // Пытаемся обновить токен в фоне
        refreshAccessToken().catch(console.error);
        return null;
    }

    return token;
};

/**
 * Получает токен обновления из localStorage
 * @returns Токен обновления или null, если токен не найден
 */
export const getRefreshToken = (): string | null => {
    return localStorage.getItem('refreshToken');
};

/**
 * Удаляет JWT токены из localStorage
 */
export const clearTokens = (): void => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
};

/**
 * Вход в админ-панель
 * @param email Email пользователя
 * @param password Пароль пользователя
 * @returns Ответ сервера с токенами
 */
export const loginAdmin = async (email: string, password: string): Promise<{ access_token: string; refresh_token: string }> => {
    const response = await fetch(getApiUrl(adminRoutes.auth.login), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Ошибка входа: ${response.status} ${errorText}`);
    }

    const data = await response.json();
    
    // Сохраняем токены
    setTokens(data.access_token, data.refresh_token);
    
    return data;
};

/**
 * Выход из системы (логаут)
 */
export const logoutAdmin = async (): Promise<void> => {
    const refreshToken = getRefreshToken();
    const accessToken = getAccessToken();
    
    if (!refreshToken || !accessToken) {
        clearTokens();
        return;
    }
    
    try {
        const response = await fetch(getApiUrl(adminRoutes.auth.logout), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`,
            },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
        
        if (!response.ok) {
            console.error('Ошибка при выходе из системы:', response.status);
        }
    } catch (error) {
        console.error('Ошибка при выходе из системы:', error);
    } finally {
        clearTokens();
    }
};

/**
 * Обновляет токен доступа, используя токен обновления
 * @returns Новая пара токенов
 */
export const refreshAccessToken = async (): Promise<{ access_token: string; refresh_token: string } | null> => {
    const refreshToken = getRefreshToken();
    
    if (!refreshToken) {
        return null;
    }
    
    try {
        const response = await fetch(getApiUrl(adminRoutes.auth.refresh), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
        
        if (!response.ok) {
            // Если ошибка обновления токена, очищаем хранилище
            clearTokens();
            throw new Error(`Ошибка обновления токена: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Сохраняем новые токены
        setTokens(data.access_token, data.refresh_token);
        
        return data;
    } catch (error) {
        console.error('Ошибка при обновлении токена:', error);
        clearTokens();
        return null;
    }
};

/**
 * Изменяет пароль пользователя
 * @param currentPassword Текущий пароль
 * @param newPassword Новый пароль
 */
export const changePassword = async (currentPassword: string, newPassword: string): Promise<void> => {
    const token = getAccessToken();
    
    if (!token) {
        throw new Error('Необходима авторизация');
    }
    
    const response = await fetch(getApiUrl(adminRoutes.auth.changePassword), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
        }),
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Ошибка изменения пароля: ${response.status} ${errorText}`);
    }
};