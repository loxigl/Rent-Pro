from src.api.auth import router as auth_router
from src.api.apartments import router as apartment_router
from src.api.images import router as image_router
from src.api.bookings import router as bookings_router
from src.api.settings import router as settings_router
from src.api.admin import admin_router

__all__ = [
    'auth_router',
    'apartment_router',
    'image_router',
    'bookings_router',
    'settings_router',
    'admin_router',
]
