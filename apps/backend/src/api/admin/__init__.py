from fastapi import APIRouter

from src.api.admin.auth import router as auth_router

# Импортируем остальные роутеры по мере их реализации
# from src.api.admin.apartments import router as apartments_router
# from src.api.admin.photos import router as photos_router
# from src.api.admin.events import router as events_router

# Создаем общий роутер для админ-панели
admin_router = APIRouter(prefix="/admin/api/v1")

# Подключаем отдельные роутеры
admin_router.include_router(auth_router)
# admin_router.include_router(apartments_router)
# admin_router.include_router(photos_router)
# admin_router.include_router(events_router)

__all__ = ["admin_router"]
