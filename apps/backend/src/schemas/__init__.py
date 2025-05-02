from src.schemas.apartment import (
    ApartmentBase, ApartmentCreate, ApartmentUpdate, ApartmentInList,
    ApartmentDetail, PaginatedApartments, ApartmentPhoto, ApartmentPhotoBase,
    ApartmentPhotoCreate
)
from src.schemas.booking import (
    BookingBase, BookingCreate, BookingUpdate, BookingStatusUpdate,
    BookingInDB, BookingResponse, BookingListResponse
)
from src.schemas.settings import (
    SystemSettingsBase, SystemSettingsUpdate, SystemSettingsInDB,
    SystemSettingsResponse, BookingGlobalToggle
)

__all__ = [
    # Квартиры
    "ApartmentBase", "ApartmentCreate", "ApartmentUpdate", "ApartmentInList",
    "ApartmentDetail", "PaginatedApartments", "ApartmentPhoto", "ApartmentPhotoBase",
    "ApartmentPhotoCreate",
    
    # Бронирования
    "BookingBase", "BookingCreate", "BookingUpdate", "BookingStatusUpdate",
    "BookingInDB", "BookingResponse", "BookingListResponse",
    
    # Настройки системы
    "SystemSettingsBase", "SystemSettingsUpdate", "SystemSettingsInDB",
    "SystemSettingsResponse", "BookingGlobalToggle"
]