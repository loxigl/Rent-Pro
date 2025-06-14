import { getApiUrl } from '../config';
import { adminRoutes } from '../routes';
import { getAccessToken } from '@/lib/utils/admin/jwt';
import { BookingStatus } from '../types';

// Заголовки для запросов, включая токен авторизации
const getHeaders = () => {
  const token = getAccessToken();
  if (!token) {
    throw new Error('Необходима авторизация');
  }
  
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
};

// Параметры получения списка бронирований
export interface GetBookingsParams {
  page?: number;
  limit?: number;
  status?: BookingStatus;
  apartment_id?: number;
  client_name?: string;
  from_date?: string;
  to_date?: string;
}

// Тип для обновления статуса бронирования
export interface BookingStatusUpdate {
  status: BookingStatus;
  admin_comment?: string;
}

/**
 * Получить список бронирований с фильтрацией и пагинацией
 */
export async function getBookings(params: GetBookingsParams = {}) {
  try {
    const searchParams = new URLSearchParams();
    
    // Добавляем все параметры в строку запроса
    if (params.page !== undefined) searchParams.append('skip', ((params.page - 1) * (params.limit || 10)).toString());
    if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
    if (params.status) searchParams.append('status', params.status);
    if (params.apartment_id) searchParams.append('apartment_id', params.apartment_id.toString());
    if (params.client_name) searchParams.append('client_name', params.client_name);
    if (params.from_date) searchParams.append('from_date', params.from_date);
    if (params.to_date) searchParams.append('to_date', params.to_date);
    
    const response = await fetch(`${getApiUrl(adminRoutes.bookings.list)}?${searchParams.toString()}`, {
      headers: getHeaders(),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Ошибка при получении списка бронирований: ${response.status} ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Ошибка при получении списка бронирований:', error);
    throw error;
  }
}

/**
 * Получить детальную информацию о бронировании по ID
 */
export async function getBookingById(id: number) {
  try {
    const response = await fetch(getApiUrl(adminRoutes.bookings.detail(id)), {
      headers: getHeaders(),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Ошибка при получении бронирования #${id}: ${response.status} ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Ошибка при получении бронирования #${id}:`, error);
    throw error;
  }
}

/**
 * Обновить данные бронирования
 */
export async function updateBooking(id: number, data: any) {
  try {
    const response = await fetch(getApiUrl(adminRoutes.bookings.update(id)), {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Ошибка при обновлении бронирования #${id}: ${response.status} ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Ошибка при обновлении бронирования #${id}:`, error);
    throw error;
  }
}

/**
 * Обновить статус бронирования
 */
export async function updateBookingStatus(id: number, data: BookingStatusUpdate) {
  try {
    const response = await fetch(getApiUrl(adminRoutes.bookings.updateStatus(id)), {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Ошибка при обновлении статуса бронирования #${id}: ${response.status} ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Ошибка при обновлении статуса бронирования #${id}:`, error);
    throw error;
  }
}

/**
 * Удалить бронирование
 */
export async function deleteBooking(id: number) {
  try {
    const response = await fetch(getApiUrl(adminRoutes.bookings.delete(id)), {
      method: 'DELETE',
      headers: getHeaders(),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Ошибка при удалении бронирования #${id}: ${response.status} ${errorText}`);
    }
    
    return true;
  } catch (error) {
    console.error(`Ошибка при удалении бронирования #${id}:`, error);
    throw error;
  }
} 