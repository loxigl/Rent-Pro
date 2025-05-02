/**
 * API-клиент для работы с настройками системы
 */

import { getApiUrl } from './config';
import { publicRoutes } from './routes';

/**
 * Интерфейс для настроек системы
 */
export interface SystemSettings {
  booking_globally_enabled: boolean;
  support_phone: string;
  support_email: string;
}

/**
 * Получить публичные настройки системы
 */
export async function getPublicSettings(): Promise<SystemSettings> {
  try {
    const response = await fetch(getApiUrl(publicRoutes.settings.public));
    
    if (!response.ok) {
      throw new Error(`Ошибка загрузки настроек: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Ошибка при загрузке публичных настроек:', error);
    
    // Возвращаем настройки по умолчанию при ошибке
    return {
      booking_globally_enabled: true,
      support_phone: '+7 (928) 123-45-67',
      support_email: 'support@avitorentpro.ru'
    };
  }
} 