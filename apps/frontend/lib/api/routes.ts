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
    search: '/apartments/search',
  },
  // Бронирования
  bookings: {
    create: '/bookings',
    cancel: (id: number) => `/bookings/${id}/cancel`,
  },
  // Публичные настройки
  settings: {
    public: '/settings/public'
  }
};

// Маршруты для админки
export const adminRoutes = {
  // Аутентификация
  auth: {
    login: '/auth/admin/login',
    logout: '/auth/logout',
    refresh: '/auth/refresh',
  },
  // Управление квартирами
  apartments: {
    list: '/admin/api/v1/apartments',
    detail: (id: number) => `/admin/api/v1/apartments/${id}`,
    create: '/admin/api/v1/apartments',
    update: (id: number) => `/admin/api/v1/apartments/${id}`,
    delete: (id: number) => `/admin/api/v1/apartments/${id}`,
  },
  // Управление фотографиями
  photos: {
    upload: '/admin/api/v1/photos',
    delete: (id: number) => `/admin/api/v1/photos/${id}`,
    update: (id: number) => `/admin/api/v1/photos/${id}`,
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
  },
  // Управление бронированиями
  bookings: {
    list: '/admin/api/v1/bookings',
    detail: (id: number) => `/admin/api/v1/bookings/${id}`,
    update: (id: number) => `/admin/api/v1/bookings/${id}`,
    delete: (id: number) => `/admin/api/v1/bookings/${id}`,
  },
  // Статистика
  stats: {
    dashboard: '/admin/api/v1/stats',
  },
  // Настройки системы
  settings: {
    get: '/admin/api/v1/settings',
    update: '/admin/api/v1/settings',
  }
}; 