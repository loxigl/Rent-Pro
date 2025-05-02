import { API_BASE_URL } from './config';

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
export async function getSystemSettings(): Promise<SystemSettings> {
  try {
    const response = await fetch(`${API_BASE_URL}/settings/public`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store'
    });

    if (!response.ok) {
      throw new Error(`Ошибка при получении настроек системы: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Ошибка при получении настроек системы:', error);
    // Возвращаем значения по умолчанию в случае ошибки
    return {
      booking_globally_enabled: true,
      support_phone: '+7 (928) 123-45-67',
      support_email: 'support@avitorentpro.ru'
    };
  }
} 