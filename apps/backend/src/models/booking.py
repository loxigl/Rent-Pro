from src.db.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum


class BookingStatus(str, enum.Enum):
    """Статусы бронирования"""
    PENDING = "pending"  # Ожидает подтверждения
    CONFIRMED = "confirmed"  # Подтверждено
    CANCELLED = "cancelled"  # Отменено
    COMPLETED = "completed"  # Завершено


class Booking(Base):
    """Модель бронирования квартиры."""
    __tablename__ = "booking"

    id = Column(Integer, primary_key=True, index=True)
    apartment_id = Column(Integer, ForeignKey("apartment.id", ondelete="CASCADE"), nullable=False)
    
    # Информация о клиенте
    client_name = Column(String(100), nullable=False)
    client_phone = Column(String(20), nullable=False)
    client_email = Column(String(100), nullable=True)
    client_comment = Column(Text, nullable=True)
    
    # Информация о бронировании
    check_in_date = Column(DateTime(timezone=True), nullable=False)
    check_out_date = Column(DateTime(timezone=True), nullable=False)
    guests_count = Column(Integer, nullable=False, default=1)
    
    # Статус и метаданные
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    admin_comment = Column(Text, nullable=True)  # Комментарий администратора
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Отношение многие-к-одному с квартирой
    apartment = relationship("Apartment", back_populates="bookings")

    # Создание индексов
    __table_args__ = (
        Index('idx_booking_dates', check_in_date, check_out_date),
        Index('idx_booking_status', status),
        Index('idx_booking_apartment', apartment_id),
    ) 