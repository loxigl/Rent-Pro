from src.models.apartment import Apartment, ApartmentPhoto
from src.models.auth import User, RolePermission
from src.models.event_log import EventLog, EventType, EntityType
from src.models.booking import Booking, BookingStatus
from src.models.settings import SystemSettings

__all__ = [
    # Основные модели
    'Apartment',
    'ApartmentPhoto',

    # Модели аутентификации и авторизации
    'User',
    'RolePermission',
    
    # Модели бронирования
    'Booking',
    'BookingStatus',
    
    # Настройки системы
    'SystemSettings',

    # Журнал событий
    'EventLog',
    'EventType',
    'EntityType'
]
