from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from requests import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.models import Booking, Apartment, SystemSettings
from src.schemas import BookingCreate, BookingResponse, BookingListResponse
from src.services.event_log_service import log_action
from src.models.event_log import EventType, EntityType
from src.services.email_service import send_booking_created_notification

router = APIRouter(
    prefix="/api/v1/bookings",
    tags=["bookings"]
)


@router.post("", response_model=BookingResponse, status_code=201)
async def create_booking(
        booking: BookingCreate,
        db: Session = Depends(get_db)
):
    """
    Создать новое бронирование квартиры.
    """
    # Проверяем, что бронирование глобально включено
    settings = db.execute(select(SystemSettings).limit(1))
    system_settings = settings.scalars().first()

    if not system_settings or not system_settings.booking_globally_enabled:
        raise HTTPException(
            status_code=403,
            detail="Бронирование временно отключено."
        )

    # Проверяем, что квартира существует и активна
    apartment_query = select(Apartment).where(
        and_(
            Apartment.id == booking.apartment_id,
            Apartment.active == True,
            Apartment.booking_enabled == True
        )
    )
    result = db.execute(apartment_query)
    apartment = result.scalars().first()

    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Квартира не найдена или недоступна для бронирования."
        )

    # Проверяем, что даты не заняты другими бронированиями
    overlap_query = select(func.count(Booking.id)).where(
        and_(
            Booking.apartment_id == booking.apartment_id,
            Booking.status.in_(["pending", "confirmed"]),
            # Проверка пересечения дат
            and_(
                Booking.check_in_date < booking.check_out_date,
                Booking.check_out_date > booking.check_in_date
            )
        )
    )
    result = db.execute(overlap_query)
    booking_count = result.scalar()

    if booking_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Выбранные даты уже заняты. Пожалуйста, выберите другие даты."
        )

    # Создаем новое бронирование
    db_booking = Booking(
        apartment_id=booking.apartment_id,
        client_name=booking.client_name,
        client_phone=booking.client_phone,
        client_email=booking.client_email,
        client_comment=booking.client_comment,
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
        guests_count=booking.guests_count
    )

    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)


    # Логируем событие
    log_action(
        db=db,
        entity_type=EntityType.BOOKING,
        entity_id=db_booking.id,
        event_type=EventType.CREATED,
        description=f"Создано новое бронирование от {booking.client_name}"
    )

    # Отправляем уведомление администратору о новом бронировании
    await send_booking_created_notification(
        booking_id=db_booking.id,
        client_name=db_booking.client_name,
        client_email=db_booking.client_email or "",
        client_phone=db_booking.client_phone,
        apartment_title=apartment.title,
        check_in_date=db_booking.check_in_date,
        check_out_date=db_booking.check_out_date,
        guests_count=db_booking.guests_count
    )

    return db_booking


@router.get("/check-availability", response_model=bool)
async def check_availability(
        apartment_id: int,
        check_in: datetime,
        check_out: datetime,
        db: Session = Depends(get_db)
):
    """
    Проверить доступность квартиры для бронирования на указанные даты.
    """
    # Проверяем, что бронирование глобально включено
    settings = db.execute(select(SystemSettings).limit(1))
    system_settings = settings.scalars().first()

    if not system_settings or not system_settings.booking_globally_enabled:
        return False

    # Проверяем, что квартира существует и активна
    apartment_query = select(Apartment).where(
        and_(
            Apartment.id == apartment_id,
            Apartment.active == True,
            Apartment.booking_enabled == True
        )
    )
    result = db.execute(apartment_query)
    apartment = result.scalars().first()

    if not apartment:
        return False

    # Проверяем, что даты не заняты другими бронированиями
    overlap_query = select(func.count(Booking.id)).where(
        and_(
            Booking.apartment_id == apartment_id,
            Booking.status.in_(["pending", "confirmed"]),
            # Проверка пересечения дат
            and_(
                Booking.check_in_date < check_out,
                Booking.check_out_date > check_in
            )
        )
    )
    result = db.execute(overlap_query)
    booking_count = result.scalar()

    # Возвращаем доступность (если нет пересечений с другими бронированиями)
    return booking_count == 0
