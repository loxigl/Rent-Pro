from fastapi import APIRouter

from src.api.admin.auth import router as auth_router
from src.api.admin.apartments import router as apartments_router
from src.api.admin.photos import router as photos_router
from src.api.admin.events import router as events_router
from src.api.admin.bookings import router as bookings_router
from src.api.admin.settings import router as settings_router

# Создаем общий роутер для админ-панели
admin_router = APIRouter(prefix="/admin/api/v1")

# Подключаем отдельные роутеры
admin_router.include_router(auth_router)
admin_router.include_router(apartments_router)
admin_router.include_router(photos_router)
admin_router.include_router(events_router)
admin_router.include_router(bookings_router)
admin_router.include_router(settings_router)

__all__ = ["admin_router"]
