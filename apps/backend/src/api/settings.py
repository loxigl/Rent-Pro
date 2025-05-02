from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.database import get_db
from src.models import SystemSettings
from src.schemas import SystemSettingsBase as SystemSettingsPublic

router = APIRouter(
    prefix="/api/v1/settings",
    tags=["settings"]
)


@router.get("/public", response_model=SystemSettingsPublic)
async def get_public_settings(
        db: AsyncSession = Depends(get_db)
):
    """
    Получить публичные настройки системы.
    """
    result = await db.execute(select(SystemSettings).limit(1))
    settings = result.scalars().first()

    # Если настройки не найдены, возвращаем значения по умолчанию
    if not settings:
        return {
            "booking_globally_enabled": True,
            "support_phone": "+7 (928) 123-45-67",
            "support_email": "support@avitorentpro.ru"
        }

    return settings
