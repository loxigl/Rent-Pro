from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class SystemSettingsBase(BaseModel):
    """Базовая схема настроек системы."""
    booking_globally_enabled: bool
    support_phone: str
    support_email: str


class SystemSettingsCreate(SystemSettingsBase):
    """Схема для создания настроек системы."""
    pass


class SystemSettingsUpdate(BaseModel):
    """Схема для обновления настроек системы."""
    booking_globally_enabled: Optional[bool] = None
    support_phone: Optional[str] = None
    support_email: Optional[str] = None


class SystemSettingsResponse(SystemSettingsBase):
    """Схема для ответа с настройками системы."""
    id: int

    class Config:
        orm_mode = True


class SystemSettingsPublic(BaseModel):
    """Публичная схема настроек системы."""
    booking_globally_enabled: bool
    support_phone: str
    support_email: str

    class Config:
        orm_mode = True


class BookingGlobalToggle(BaseModel):
    """Схема для включения/выключения глобальной функции бронирования."""
    enabled: bool


class SystemSettingsInDB(SystemSettingsBase):
    """Схема системных настроек из БД."""
    id: int
    updated_at: datetime
    updated_by: Optional[str] = None
    
    class Config:
        orm_mode = True


class SystemSettingsResponse(SystemSettingsInDB):
    """Схема ответа с данными системных настроек."""
    pass 