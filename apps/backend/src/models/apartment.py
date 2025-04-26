from src.db.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float, UniqueConstraint, Index, \
    JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Apartment(Base):
    """Модель квартиры."""
    __tablename__ = "apartment"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, unique=True, index=True)
    price_rub = Column(Integer, nullable=False)
    rooms = Column(Integer, nullable=False)
    floor = Column(Integer, nullable=False)
    area_m2 = Column(Float, nullable=False)
    address = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Отношение один-ко-многим с фотографиями
    photos = relationship("ApartmentPhoto", back_populates="apartment", cascade="all, delete-orphan")

    # Создание индекса для активных квартир
    __table_args__ = (
        Index('idx_apartment_active', active, postgresql_where=active.is_(True)),
    )


class ApartmentPhoto(Base):
    """Модель фотографии квартиры."""
    __tablename__ = "apartment_photo"

    id = Column(Integer, primary_key=True, index=True)
    apartment_id = Column(Integer, ForeignKey("apartment.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(255), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    metadata = Column(JSONB, nullable=True)  # Метаданные для хранения информации о вариантах изображения
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Отношение многие-к-одному с квартирой
    apartment = relationship("Apartment", back_populates="photos")

    # Уникальное ограничение для сортировки фото
    __table_args__ = (
        UniqueConstraint('apartment_id', 'sort_order', name='uq_ap_photo_sort'),
    )
