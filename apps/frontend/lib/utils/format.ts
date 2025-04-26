/**
 * Форматирует цену в рублях со знаком ₽
 */
export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
  }).format(price);
};

/**
 * Форматирует строку комнат (1 комн, 2 комн)
 */
export const formatRooms = (rooms: number): string => {
  if (rooms === 0) return 'Студия';

  const roomForms = ['комната', 'комнаты', 'комнат'];
  let form: string;

  if (rooms % 100 > 10 && rooms % 100 < 20) {
    form = roomForms[2];
  } else if (rooms % 10 === 1) {
    form = roomForms[0];
  } else if (rooms % 10 >= 2 && rooms % 10 <= 4) {
    form = roomForms[1];
  } else {
    form = roomForms[2];
  }

  return `${rooms} ${form}`;
};

/**
 * Форматирует площадь в квадратных метрах
 */
export const formatArea = (area: number): string => {
  return `${area} м²`;
};

/**
 * Форматирует этаж
 */
export const formatFloor = (floor: number): string => {
  return `${floor} эт.`;
};

/**
 * Создает строку характеристик квартиры для карточки
 */
export const formatApartmentFeatures = (rooms: number, area: number, floor: number): string => {
  const roomsText = rooms === 0 ? 'Студия' : `${rooms} комн`;
  return `${roomsText} • ${area} м² • ${floor} эт.`;
};

/**
 * Форматирует дату в российском формате
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

/**
 * Обрезает текст до указанной длины и добавляет многоточие
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

/**
 * Генерирует URL телефона для звонка
 */
export const formatPhoneUrl = (phone: string): string => {
  return `tel:${phone.replace(/\D/g, '')}`;
};

/**
 * Генерирует URL для Telegram
 */
export const formatTelegramUrl = (username: string): string => {
  return `https://t.me/${username.replace('@', '')}`;
};