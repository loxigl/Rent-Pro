import { getApiUrl } from './config';
import { publicRoutes } from './routes';

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
  try {
    const formattedData = {
      ...data,
      check_in_date: data.check_in_date.toISOString(),
      check_out_date: data.check_out_date.toISOString(),
    };

    const response = await fetch(getApiUrl(publicRoutes.bookings.create), {
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
  } catch (error) {
    console.error('Ошибка при создании бронирования:', error);
    throw error;
  }
}

/**
 * Проверить доступность дат для конкретной квартиры
 */
export async function checkAvailability(
  apartmentId: number, 
  checkIn: Date, 
  checkOut: Date
): Promise<boolean> {
  try {
    const params = new URLSearchParams({
      apartment_id: apartmentId.toString(),
      check_in: checkIn.toISOString(),
      check_out: checkOut.toISOString(),
    });

    const response = await fetch(`${getApiUrl(publicRoutes.bookings.checkAvailability)}?${params}`);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Ошибка при проверке доступности дат: ${response.status} ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Ошибка при проверке доступности дат:', error);
    throw error;
  }
} 