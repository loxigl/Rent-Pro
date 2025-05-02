// Типы статусов бронирования
export type BookingStatus = 'pending' | 'confirmed' | 'cancelled' | 'completed';

// Базовый тип бронирования
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
  status: BookingStatus;
  admin_comment?: string;
  created_at: string;
  updated_at: string;
  apartment?: {
    id: number;
    title: string;
  };
}

// Тип для создания бронирования
export interface CreateBookingData {
  apartment_id: number;
  client_name: string;
  client_phone: string;
  client_email?: string;
  client_comment?: string;
  check_in_date: Date | string;
  check_out_date: Date | string;
  guests_count: number;
}

// Тип для обновления бронирования
export interface UpdateBookingData {
  client_name?: string;
  client_phone?: string;
  client_email?: string;
  client_comment?: string;
  guests_count?: number;
  admin_comment?: string;
}

// Тип для ответа со списком бронирований
export interface BookingListResponse {
  total: number;
  items: Booking[];
}

// Типы, связанные с настройками системы
export interface SystemSettings {
  id: number;
  booking_globally_enabled: boolean;
  settings_data?: Record<string, any>;
  updated_at: string;
  updated_by?: string;
}

// Тип для обновления глобальных настроек бронирования
export interface BookingGlobalToggle {
  enabled: boolean;
  updated_by?: string;
}

// Тип для обновления возможности бронирования для отдельной квартиры
export interface ApartmentBookingToggle {
  apartment_id: number;
  booking_enabled: boolean;
} 