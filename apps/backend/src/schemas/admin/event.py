from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class EventLogDetail(BaseModel):
    """Схема детальной информации о событии для админ-панели."""
    id: UUID
    timestamp: datetime
    user_id: Optional[int] = None
    user_email: Optional[str] = None  # Email пользователя, добавляется при запросе
    event_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class EventLogListResponse(BaseModel):
    """Схема ответа со списком событий для админ-панели."""
    items: List[EventLogDetail]
    total: int
    page: int
    page_size: int


class EventLogFilter(BaseModel):
    """Схема фильтра для журнала событий."""
    user_id: Optional[int] = None
    event_type: Optional[str] = None
    entity_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None