from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import joinedload

from src.db.database import get_db
from src.models import Booking, BookingStatus, Apartment, SystemSettings
from src.schemas import (
    BookingResponse, BookingListResponse, BookingUpdate, BookingStatusUpdate,
    SystemSettingsResponse, BookingGlobalToggle
)
from src.models.event_log import EventType, EntityType
from src.services.event_log_service import log_action
from src.middleware.auth import get_current_active_user, check_permissions
from src.models.auth.role import RolePermission
from src.services.email_service import send_booking_confirmation, send_booking_cancellation

router = APIRouter(
    prefix="/api/v1/admin/bookings",
    tags=["admin", "bookings"]
)


@router.get("", response_model=BookingListResponse)
async def list_bookings(
        status: Optional[BookingStatus] = None,
        apartment_id: Optional[int] = None,
        client_name: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        _: dict = Depends(check_permissions(required_permissions=[RolePermission.MANAGE_BOOKINGS]))
):
    """
    Получить список бронирований с фильтрацией.
    """
    # Базовый запрос
    query = select(Booking).options(joinedload(Booking.apartment))
    count_query = select(func.count(Booking.id))

    # Применяем фильтры, если они указаны
    if status:
        query = query.where(Booking.status == status)
        count_query = count_query.where(Booking.status == status)

    if apartment_id:
        query = query.where(Booking.apartment_id == apartment_id)
        count_query = count_query.where(Booking.apartment_id == apartment_id)

    if client_name:
        query = query.where(Booking.client_name.ilike(f"%{client_name}%"))
        count_query = count_query.where(Booking.client_name.ilike(f"%{client_name}%"))

    if from_date:
        query = query.where(Booking.check_in_date >= from_date)
        count_query = count_query.where(Booking.check_in_date >= from_date)

    if to_date:
        query = query.where(Booking.check_out_date <= to_date)
        count_query = count_query.where(Booking.check_out_date <= to_date)

    # Сортировка и пагинация
    query = query.order_by(desc(Booking.created_at)).offset(skip).limit(limit)

    # Выполняем запросы
    bookings = await db.execute(query)
    total_count = await db.execute(count_query)

    return {
        "total": total_count.scalar(),
        "items": bookings.scalars().all()
    }


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
        booking_id: int = Path(..., description="ID бронирования"),
        db: AsyncSession = Depends(get_db),
        _: dict = Depends(check_permissions(required_permissions=[RolePermission.MANAGE_BOOKINGS]))
):
    """
    Получить информацию о конкретном бронировании по ID.
    """
    booking = await db.execute(
        select(Booking)
        .options(joinedload(Booking.apartment))
        .where(Booking.id == booking_id)
    )
    booking = booking.scalars().first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail=f"Бронирование с ID {booking_id} не найдено"
        )

    return booking


@router.patch("/{booking_id}", response_model=BookingResponse)
async def update_booking(
        booking_data: BookingUpdate,
        booking_id: int = Path(..., description="ID бронирования"),
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(check_permissions(required_permissions=[RolePermission.MANAGE_BOOKINGS]))
):
    """
    Обновить информацию о бронировании по ID.
    """
    # Находим бронирование
    booking_query = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(booking_query)
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail=f"Бронирование с ID {booking_id} не найдено"
        )

    # Обновляем поля, если они указаны
    update_data = booking_data.dict(exclude_unset=True)

    if update_data:
        for key, value in update_data.items():
            setattr(booking, key, value)

        # Логируем изменения
        await log_action(
            db=db,
            entity_type=EntityType.BOOKING,
            entity_id=booking.id,
            event_type=EventType.UPDATED,
            description=f"Обновлено бронирование #{booking_id} пользователем {current_user.get('username')}",
            user_id=current_user.get('id')
        )

        await db.commit()
        await db.refresh(booking)

    return booking


@router.patch("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
        status_data: BookingStatusUpdate,
        booking_id: int = Path(..., description="ID бронирования"),
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(check_permissions(required_permissions=[RolePermission.MANAGE_BOOKINGS]))
):
    """
    Обновить статус бронирования (подтвердить/отменить).
    """
    # Находим бронирование с информацией о квартире
    booking_query = select(Booking).options(joinedload(Booking.apartment)).where(Booking.id == booking_id)
    result = await db.execute(booking_query)
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail=f"Бронирование с ID {booking_id} не найдено"
        )

    # Изменение статуса должно быть логичным
    current_status = booking.status
    new_status = status_data.status

    # Сохраняем предыдущий статус для логирования
    old_status = booking.status

    # Обновляем статус и комментарий администратора
    booking.status = new_status
    if status_data.admin_comment:
        booking.admin_comment = status_data.admin_comment

    # Логируем изменение статуса
    await log_action(
        db=db,
        entity_type=EntityType.BOOKING,
        entity_id=booking.id,
        event_type=EventType.STATUS_CHANGED,
        description=f"Статус бронирования #{booking_id} изменен с '{old_status}' на '{new_status}' пользователем {current_user.get('username')}",
        metadata={
            "old_status": old_status,
            "new_status": new_status
        },
        user_id=current_user.get('id')
    )

    await db.commit()
    await db.refresh(booking)

    # Отправляем уведомление по email при изменении статуса
    if booking.client_email:
        # Если статус меняется на "подтверждено"
        if new_status == BookingStatus.CONFIRMED and old_status != BookingStatus.CONFIRMED:
            await send_booking_confirmation(
                booking_id=booking.id,
                client_name=booking.client_name,
                client_email=booking.client_email,
                apartment_title=booking.apartment.title,
                check_in_date=booking.check_in_date,
                check_out_date=booking.check_out_date,
                guests_count=booking.guests_count
            )

        # Если статус меняется на "отменено"
        elif new_status == BookingStatus.CANCELLED and old_status != BookingStatus.CANCELLED:
            await send_booking_cancellation(
                booking_id=booking.id,
                client_name=booking.client_name,
                client_email=booking.client_email,
                apartment_title=booking.apartment.title,
                check_in_date=booking.check_in_date,
                check_out_date=booking.check_out_date
            )

    return booking


@router.delete("/{booking_id}", status_code=204)
async def delete_booking(
        booking_id: int = Path(..., description="ID бронирования"),
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(check_permissions(required_permissions=[RolePermission.MANAGE_BOOKINGS]))
):
    """
    Удалить бронирование по ID.
    """
    booking_query = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(booking_query)
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail=f"Бронирование с ID {booking_id} не найдено"
        )

    # Логируем удаление
    await log_action(
        db=db,
        entity_type=EntityType.BOOKING,
        entity_id=booking.id,
        event_type=EventType.DELETED,
        description=f"Удалено бронирование #{booking_id} пользователем {current_user.get('username')}",
        user_id=current_user.get('id')
    )

    await db.delete(booking)
    await db.commit()

    return None
