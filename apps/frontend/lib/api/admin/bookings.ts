import { API_BASE_URL } from '../config';
import { BookingStatus } from '../types';

// Заголовки для запросов, включая токен авторизации
const getHeaders = () => {
  const token = localStorage.getItem('accessToken');
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
  const searchParams = new URLSearchParams();
  
  // Добавляем все параметры в строку запроса
  if (params.page !== undefined) searchParams.append('skip', ((params.page - 1) * (params.limit || 10)).toString());
  if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
  if (params.status) searchParams.append('status', params.status);
  if (params.apartment_id) searchParams.append('apartment_id', params.apartment_id.toString());
  if (params.client_name) searchParams.append('client_name', params.client_name);
  if (params.from_date) searchParams.append('from_date', params.from_date);
  if (params.to_date) searchParams.append('to_date', params.to_date);
  
  const response = await fetch(`${API_BASE_URL}/admin/bookings?${searchParams.toString()}`, {
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Ошибка при получении списка бронирований');
  }
  
  return await response.json();
}

/**
 * Получить детальную информацию о бронировании по ID
 */
export async function getBookingById(id: number) {
  const response = await fetch(`${API_BASE_URL}/admin/bookings/${id}`, {
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Ошибка при получении бронирования #${id}`);
  }
  
  return await response.json();
}

/**
 * Обновить данные бронирования
 */
export async function updateBooking(id: number, data: any) {
  const response = await fetch(`${API_BASE_URL}/admin/bookings/${id}`, {
    method: 'PATCH',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error(`Ошибка при обновлении бронирования #${id}`);
  }
  
  return await response.json();
}

/**
 * Обновить статус бронирования
 */
export async function updateBookingStatus(id: number, data: BookingStatusUpdate) {
  const response = await fetch(`${API_BASE_URL}/admin/bookings/${id}/status`, {
    method: 'PATCH',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error(`Ошибка при обновлении статуса бронирования #${id}`);
  }
  
  return await response.json();
}

/**
 * Удалить бронирование
 */
export async function deleteBooking(id: number) {
  const response = await fetch(`${API_BASE_URL}/admin/bookings/${id}`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Ошибка при удалении бронирования #${id}`);
  }
  
  return true;
}

/**
 * Получить статистику по бронированиям
 */
export async function getBookingsStats() {
  const response = await fetch(`${API_BASE_URL}/admin/bookings/stats`, {
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Ошибка при получении статистики бронирований');
  }
  
  return await response.json();
} 