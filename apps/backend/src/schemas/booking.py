from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator, EmailStr
from src.models.booking import BookingStatus


class BookingBase(BaseModel):
    """Базовая схема бронирования."""
    apartment_id: int = Field(..., description="ID квартиры")
    client_name: str = Field(..., description="Имя клиента", max_length=100)
    client_phone: str = Field(..., description="Телефон клиента", max_length=20)
    client_email: Optional[EmailStr] = Field(None, description="Email клиента")
    client_comment: Optional[str] = Field(None, description="Комментарий клиента")
    check_in_date: datetime = Field(..., description="Дата заезда")
    check_out_date: datetime = Field(..., description="Дата выезда")
    guests_count: int = Field(1, description="Количество гостей", ge=1)

    @classmethod
    @validator('check_out_date')
    def check_dates(cls, v, values):
        if 'check_in_date' in values and v <= values['check_in_date']:
            raise ValueError('Дата выезда должна быть позже даты заезда')
        return v


class BookingCreate(BookingBase):
    """Схема для создания бронирования."""
    pass


class BookingUpdate(BaseModel):
    """Схема для обновления бронирования."""
    client_name: Optional[str] = Field(None, description="Имя клиента", max_length=100)
    client_phone: Optional[str] = Field(None, description="Телефон клиента", max_length=20)
    client_email: Optional[EmailStr] = Field(None, description="Email клиента")
    client_comment: Optional[str] = Field(None, description="Комментарий клиента")
    check_in_date: Optional[datetime] = Field(None, description="Дата заезда")
    check_out_date: Optional[datetime] = Field(None, description="Дата выезда")
    guests_count: Optional[int] = Field(None, description="Количество гостей", ge=1)
    admin_comment: Optional[str] = Field(None, description="Комментарий администратора")


class BookingStatusUpdate(BaseModel):
    """Схема для обновления статуса бронирования."""
    status: BookingStatus = Field(..., description="Статус бронирования")
    admin_comment: Optional[str] = Field(None, description="Комментарий администратора")


class BookingInDB(BookingBase):
    """Схема бронирования из БД."""
    id: int
    status: BookingStatus
    admin_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BookingResponse(BookingInDB):
    """Схема ответа с данными бронирования."""
    pass


class BookingListResponse(BaseModel):
    """Схема ответа со списком бронирований."""
    total: int
    items: List[BookingResponse]

    class Config:
        orm_mode = True
