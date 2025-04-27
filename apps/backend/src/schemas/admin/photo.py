from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class PhotoAdminBase(BaseModel):
    """Базовая схема фотографии для админ-панели."""
    apartment_id: int
    url: str
    sort_order: int
    is_cover: bool = False


class PhotoAdminCreate(PhotoAdminBase):
    """Схема для создания записи о фотографии через админ-панель."""
    pass


class PhotoAdminUpdate(BaseModel):
    """Схема для обновления данных фотографии через админ-панель."""
    sort_order: Optional[int] = None
    is_cover: Optional[bool] = None


class PhotoAdminDetail(PhotoAdminBase):
    """Схема детальной информации о фотографии для админ-панели."""
    id: int
    created_at: datetime
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class PhotoAdminListItem(BaseModel):
    """Схема элемента списка фотографий для админ-панели."""
    id: int
    apartment_id: int
    url: str
    sort_order: int
    is_cover: bool
    created_at: datetime
    thumbnail_url: Optional[str] = None  # URL для миниатюры

    class Config:
        from_attributes = True


class PhotoAdminListResponse(BaseModel):
    """Схема ответа со списком фотографий для админ-панели."""
    items: List[PhotoAdminListItem]
    total: int


class BulkPhotoUpdateRequest(BaseModel):
    """Схема для массового обновления порядка фотографий."""
    updates: List[dict] = Field(..., description="Список обновлений в формате {id: int, sort_order: int}")


class PhotoUploadResponse(BaseModel):
    """Схема ответа после загрузки фотографии."""
    id: int
    url: str
    thumbnail_url: Optional[str] = None
    apartment_id: int
    sort_order: int
    is_cover: bool
