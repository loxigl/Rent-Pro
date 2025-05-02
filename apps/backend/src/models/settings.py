from src.db.database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func


class SystemSettings(Base):
    """Модель глобальных настроек системы."""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True)
    
    # Глобальные настройки бронирования
    booking_globally_enabled = Column(Boolean, default=True, nullable=False)
    
    # Другие настройки системы
    settings_data = Column(JSONB, nullable=True)  # Различные настройки в формате JSON
    
    # Метаданные
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)  # Кто последний обновил настройки 