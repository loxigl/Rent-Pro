from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Схемы для фотографий квартир
class ApartmentPhotoBase(BaseModel):
    url: str
    sort_order: int


class ApartmentPhotoCreate(ApartmentPhotoBase):
    apartment_id: int


class ApartmentPhoto(ApartmentPhotoBase):
    id: int
    apartment_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Схемы для квартир
class ApartmentBase(BaseModel):
    title: str
    price_rub: int
    rooms: int
    floor: int
    area_m2: float
    address: str
    description: Optional[str] = None


class ApartmentCreate(ApartmentBase):
    active: bool = True


class ApartmentUpdate(BaseModel):
    title: Optional[str] = None
    price_rub: Optional[int] = None
    rooms: Optional[int] = None
    floor: Optional[int] = None
    area_m2: Optional[float] = None
    address: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class ApartmentInList(BaseModel):
    id: int
    title: str
    price_rub: int
    rooms: int
    floor: int
    area_m2: float
    cover_url: Optional[str] = None

    class Config:
        from_attributes = True


class ApartmentDetail(ApartmentBase):
    id: int
    active: bool
    photos: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Схема для пагинации
class PaginatedApartments(BaseModel):
    page: int
    page_size: int
    total: int
    items: List[ApartmentInList]