from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from src.db.database import get_db
from src.models import SystemSettings, Apartment
from src.schemas import SystemSettingsResponse, SystemSettingsUpdate, BookingGlobalToggle
from src.middleware.auth import check_permissions
from src.models.auth.role import RolePermission
from src.services.event_log_service import log_action
from src.models.event_log import EventType, EntityType

router = APIRouter(
    prefix="/api/v1/admin/settings",
    tags=["admin", "settings"]
)


@router.get("", response_model=SystemSettingsResponse)
async def get_system_settings(
        db: AsyncSession = Depends(get_db),
        _: dict = Depends(check_permissions(required_permissions=[RolePermission.MANAGE_SETTINGS]))
):
    """
    Получить текущие системные настройки.
    """
    settings = await db.execute(select(SystemSettings).limit(1))
    system_settings = settings.scalars().first()

    if not system_settings:
        # Если настройки не существуют, создаем их с значениями по умолчанию
        system_settings = SystemSettings(booking_globally_enabled=True)
        db.add(system_settings)
        await db.commit()
        await db.refresh(system_settings)

    return system_settings


@router.patch("", response_model=SystemSettingsResponse)
async def update_system_settings(
        settings_data: SystemSettingsUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(check_permissions(required_permissions=[RolePermission.MANAGE_SETTINGS]))
):
    """
    Обновить системные настройки.
    """
    settings_query = select(SystemSettings).limit(1)
    result = await db.execute(settings_query)
    system_settings = result.scalars().first()

    if not system_settings:
        # Если настройки не существуют, создаем их с новыми значениями
        update_data = settings_data.dict(exclude_unset=True)
        system_settings = SystemSettings(**update_data)
        db.add(system_settings)
    else:
        # Обновляем существующие настройки
        update_data = settings_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(system_settings, key, value)

    # Если указан пользователь, обновляем поле updated_by
    if current_user:
        system_settings.updated_by = current_user.get('username')

    # Логируем изменения
    await log_action(
        db=db,
        entity_type=EntityType.SYSTEM,
        entity_id=1,  # Для системных настроек используем id=1
        event_type=EventType.UPDATED,
        description=f"Обновлены системные настройки пользователем {current_user.get('username')}",
        user_id=current_user.get('id')
    )

    await db.commit()
    await db.refresh(system_settings)

    return system_settings


@router.patch("/booking-toggle", response_model=SystemSettingsResponse)
async def toggle_global_booking(
        data: BookingGlobalToggle,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(check_permissions(required_permissions=[RolePermission.MANAGE_SETTINGS]))
):
    """
    Включить/отключить возможность бронирования глобально.
    """
    settings_query = select(SystemSettings).limit(1)
    result = await db.execute(settings_query)
    system_settings = result.scalars().first()

    if not system_settings:
        # Если настройки не существуют, создаем их
        system_settings = SystemSettings(
            booking_globally_enabled=data.enabled,
            updated_by=data.updated_by or current_user.get('username')
        )
        db.add(system_settings)
    else:
        # Обновляем настройку
        system_settings.booking_globally_enabled = data.enabled
        system_settings.updated_by = data.updated_by or current_user.get('username')

    # Логируем изменение
    action = "включена" if data.enabled else "отключена"
    await log_action(
        db=db,
        entity_type=EntityType.SYSTEM,
        entity_id=1,
        event_type=EventType.UPDATED,
        description=f"Возможность бронирования глобально {action} пользователем {current_user.get('username')}",
        user_id=current_user.get('id')
    )

    await db.commit()
    await db.refresh(system_settings)

    return system_settings


@router.patch("/apartments/{apartment_id}/booking-toggle", response_model=dict)
async def toggle_apartment_booking(
        apartment_id: int = Path(..., description="ID квартиры"),
        enable: bool = True,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(check_permissions(required_permissions=[RolePermission.MANAGE_APARTMENTS]))
):
    """
    Включить/отключить возможность бронирования для конкретной квартиры.
    """
    # Проверяем наличие квартиры
    apartment_query = select(Apartment).where(Apartment.id == apartment_id)
    result = await db.execute(apartment_query)
    apartment = result.scalars().first()

    if not apartment:
        raise HTTPException(
            status_code=404,
            detail=f"Квартира с ID {apartment_id} не найдена"
        )

    # Обновляем поле booking_enabled
    apartment.booking_enabled = enable

    # Логируем изменение
    action = "включена" if enable else "отключена"
    await log_action(
        db=db,
        entity_type=EntityType.APARTMENT,
        entity_id=apartment_id,
        event_type=EventType.UPDATED,
        description=f"Возможность бронирования для квартиры #{apartment_id} {action} пользователем {current_user.get('username')}",
        user_id=current_user.get('id')
    )

    await db.commit()

    return {
        "apartment_id": apartment_id,
        "booking_enabled": enable,
        "message": f"Возможность бронирования для квартиры {apartment_id} успешно {'включена' if enable else 'отключена'}"
    }
