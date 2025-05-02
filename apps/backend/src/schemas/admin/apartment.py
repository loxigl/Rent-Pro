from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ApartmentAdminBase(BaseModel):
    """Базовая схема квартиры для админ-панели."""
    title: str = Field(..., min_length=20, max_length=120)
    price_rub: int = Field(..., ge=0)
    rooms: int = Field(..., ge=1, le=6)
    floor: int = Field(..., ge=1)
    area_m2: float = Field(..., ge=10.0, le=150.0)
    address: str = Field(..., min_length=5, max_length=255)
    description: Optional[str] = None
    active: bool = True

    @validator('title')
    @classmethod
    def title_must_not_contain_html(cls, v):
        """Проверяет, что заголовок не содержит HTML-теги."""
        if '<' in v or '>' in v:
            raise ValueError('Заголовок не может содержать HTML-теги')
        return v

    @validator('price_rub')
    @classmethod
    def price_must_be_multiple_of_50(cls, v):
        """Проверяет, что цена кратна 50."""
        if v % 50 != 0:
            raise ValueError('Цена должна быть кратна 50')
        return v


class ApartmentAdminCreate(ApartmentAdminBase):
    """Схема для создания квартиры через админ-панель."""
    pass


class ApartmentAdminUpdate(BaseModel):
    """Схема для обновления данных квартиры через админ-панель."""
    title: Optional[str] = Field(None, min_length=20, max_length=120)
    price_rub: Optional[int] = Field(None, ge=0)
    rooms: Optional[int] = Field(None, ge=1, le=6)
    floor: Optional[int] = Field(None, ge=1)
    area_m2: Optional[float] = Field(None, ge=10.0, le=150.0)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = None
    active: Optional[bool] = None

    @validator('title')
    @classmethod
    def title_must_not_contain_html(cls, v):
        """Проверяет, что заголовок не содержит HTML-теги."""
        if v is not None and ('<' in v or '>' in v):
            raise ValueError('Заголовок не может содержать HTML-теги')
        return v

    @validator('price_rub')
    @classmethod
    def price_must_be_multiple_of_50(cls, v):
        """Проверяет, что цена кратна 50."""
        if v is not None and v % 50 != 0:
            raise ValueError('Цена должна быть кратна 50')
        return v


class ApartmentAdminDetail(ApartmentAdminBase):
    """Схема детальной информации о квартире для админ-панели."""
    id: int
    photos_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApartmentAdminListItem(BaseModel):
    """Схема элемента списка квартир для админ-панели."""
    id: int
    title: str
    price_rub: int
    rooms: int
    area_m2: float
    active: bool
    photos_count: int
    cover_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ApartmentAdminListResponse(BaseModel):
    """Схема ответа со списком квартир для админ-панели."""
    items: List[ApartmentAdminListItem]
    total: int
    page: int
    page_size: int

