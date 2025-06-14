/**
 * Конфигурация API маршрутов
 * Централизованное хранение всех путей API для предотвращения дублирования и ошибок
 */

// Маршруты для публичной части приложения
export const publicRoutes = {
  // Квартиры
  apartments: {
    list: '/apartments',
    detail: (id: number) => `/apartments/${id}`,
    photos: (id: number) => `/apartments/${id}/photos`,
  },
  // Бронирования
  bookings: {
    create: '/api/v1/bookings',
    cancel: (id: number) => `/api/v1/bookings/${id}/cancel`,
    checkAvailability: '/api/v1/bookings/check-availability',
  },
  // Публичные настройки
  settings: {
    public: '/api/v1/settings/public'
  }
};

// Маршруты для админки
export const adminRoutes = {
  // Аутентификация
  auth: {
    login: '/admin/api/v1/auth/login',
    logout: '/admin/api/v1/auth/logout',
    refresh: '/admin/api/v1/auth/refresh',
    changePassword: '/admin/api/v1/auth/change-password',
  },
  // Управление квартирами
  apartments: {
    list: '/admin/api/v1/apartments',
    detail: (id: number) => `/admin/api/v1/apartments/${id}`,
    create: '/admin/api/v1/apartments',
    update: (id: number) => `/admin/api/v1/apartments/${id}`,
    delete: (id: number) => `/admin/api/v1/apartments/${id}`,
    bookingToggle: (id: number) => `/admin/api/v1/apartments/${id}/booking-toggle`,
  },
  // Управление фотографиями
  photos: {
    list: (apartmentId: number) => `/admin/api/v1/photos/${apartmentId}`,
    upload: (apartmentId: number) => `/admin/api/v1/photos/${apartmentId}/upload`,
    update: (photoId: number) => `/admin/api/v1/photos/${photoId}`,
    delete: (photoId: number) => `/admin/api/v1/photos/${photoId}`,
    bulkUpdate: '/admin/api/v1/photos/bulk-update',
  },
  // Управление пользователями
  users: {
    list: '/admin/api/v1/users',
    detail: (id: number) => `/admin/api/v1/users/${id}`,
    create: '/admin/api/v1/users',
    update: (id: number) => `/admin/api/v1/users/${id}`,
    delete: (id: number) => `/admin/api/v1/users/${id}`,
  },
  // Журнал событий
  events: {
    list: '/admin/api/v1/events',
    detail: (id: string) => `/admin/api/v1/events/${id}`,
    summary: '/admin/api/v1/events/stats/summary',
  },
  // Управление бронированиями
  bookings: {
    list: '/admin/api/v1/bookings',
    detail: (id: number) => `/admin/api/v1/bookings/${id}`,
    update: (id: number) => `/admin/api/v1/bookings/${id}`,
    delete: (id: number) => `/admin/api/v1/bookings/${id}`,
    updateStatus: (id: number) => `/admin/api/v1/bookings/${id}/status`,
  },
  // Статистика
  stats: {
    dashboard: '/admin/api/v1/stats',
  },
  // Настройки системы
  settings: {
    get: '/admin/api/v1/settings',
    update: '/admin/api/v1/settings',
    bookingToggle: '/admin/api/v1/settings/booking-toggle',
    apartmentBookingToggle: (id: number) => `/admin/api/v1/settings/apartments/${id}/booking-toggle`,
  }
}; 