import { publicRoutes, adminRoutes } from './routes';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Базовый URL для API в зависимости от окружения
export const getApiBaseUrl = () => {
  // Проверяем, работаем ли мы на клиенте (браузере)
  if (typeof window !== 'undefined') {
    // Обнаруживаем административный путь
    const isAdminPath = window.location.pathname.startsWith('/admin');
    
    // Если мы на пути /admin, формируем URL с учетом этого
    if (isAdminPath) {
      // Базовый URL для админки (без /api в конце, т.к. он будет добавлен в маршрутах)
      return `${window.location.protocol}//${window.location.host}`;
    }
  }
  
  // По умолчанию используем конфигурацию из переменных окружения
  return API_BASE_URL.endsWith('/api') ? API_BASE_URL.slice(0, -4) : API_BASE_URL;
};

// Получаем полный URL для API
export const getApiUrl = (endpoint: string): string => {
  const baseUrl = getApiBaseUrl();
  // Префикс API уже включен в базовый URL или будет добавлен в endpoint
  const apiPrefix = '/api';
  
  // Проверяем, нужно ли добавить префикс /api
  if (endpoint.startsWith('/api')) {
    // Если эндпоинт уже начинается с /api, не добавляем его повторно
    return `${baseUrl}${apiPrefix}${endpoint}`;
  } else {
    // Добавляем префикс /api к эндпоинту
    return `${baseUrl}${apiPrefix}${endpoint}`;
  }
};

// Получение URL для публичного API
export const getPublicApiUrl = (path: string): string => {
  return getApiUrl(path);
};

// Получение URL для админского API
export const getAdminApiUrl = (path: string): string => {
  return getApiUrl(path);
}; 