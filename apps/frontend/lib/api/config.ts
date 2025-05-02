import { publicRoutes, adminRoutes } from './routes';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Базовый URL для API в зависимости от окружения
export const getApiBaseUrl = () => {
  // Проверяем, работаем ли мы на клиенте (браузере)
  if (typeof window !== 'undefined') {
    // Обнаруживаем административный поддомен
    const isAdminDomain = window.location.hostname.startsWith('admin.');
    
    // Если мы на admin поддомене, формируем URL с учетом этого
    if (isAdminDomain) {
      // Базовый URL для админки
      return `${window.location.protocol}//${window.location.host}/api`;
    }
  }
  
  // По умолчанию используем конфигурацию из переменных окружения
  return API_BASE_URL;
};

// Получаем полный URL для API
export const getApiUrl = (endpoint: string): string => {
  const baseUrl = getApiBaseUrl();
  
  // Проверяем, содержит ли baseUrl уже /api
  if (baseUrl.endsWith('/api')) {
    return `${baseUrl}/v1${endpoint}`;
  } else if (baseUrl.endsWith('/api/v1')) {
    return `${baseUrl}${endpoint}`;
  } else {
    return `${baseUrl}/api/v1${endpoint}`;
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