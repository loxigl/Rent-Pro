import { API_BASE_URL } from './config';

/**
 * Интерфейс для данных создания бронирования
 */
export interface CreateBookingData {
  apartment_id: number;
  client_name: string;
  client_phone: string;
  client_email?: string;
  client_comment?: string;
  check_in_date: Date;
  check_out_date: Date;
  guests_count: number;
}

/**
 * Интерфейс бронирования, возвращаемого с сервера
 */
export interface Booking {
  id: number;
  apartment_id: number;
  client_name: string;
  client_phone: string;
  client_email?: string;
  client_comment?: string;
  check_in_date: string;
  check_out_date: string;
  guests_count: number;
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed';
  admin_comment?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Создать новое бронирование
 */
export async function createBooking(data: CreateBookingData): Promise<Booking> {
  const formattedData = {
    ...data,
    check_in_date: data.check_in_date.toISOString(),
    check_out_date: data.check_out_date.toISOString(),
  };

  const response = await fetch(`${API_BASE_URL}/bookings`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formattedData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Ошибка при создании бронирования');
  }

  return await response.json();
}

/**
 * Проверить доступность дат для конкретной квартиры
 */
export async function checkAvailability(
  apartmentId: number, 
  checkIn: Date, 
  checkOut: Date
): Promise<boolean> {
  const params = new URLSearchParams({
    apartment_id: apartmentId.toString(),
    check_in: checkIn.toISOString(),
    check_out: checkOut.toISOString(),
  });

  const response = await fetch(`${API_BASE_URL}/bookings/check-availability?${params}`);

  if (!response.ok) {
    throw new Error('Ошибка при проверке доступности дат');
  }

  return await response.json();
} 