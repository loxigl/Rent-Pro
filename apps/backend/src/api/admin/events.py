from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging

from src.db.database import get_db
from src.models.auth import User
from src.models.event_log import EventLog
from src.schemas.admin import EventLogDetail, EventLogListResponse, EventLogFilter
from src.middleware.auth import get_current_active_user
from src.middleware.acl import require_events_read
from src.services.event_log_service import get_events, get_event_by_id, get_event_stats

router = APIRouter(prefix="/events", tags=["admin-events"])
logger = logging.getLogger(__name__)


@router.get("", response_model=EventLogListResponse)
async def get_event_log(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        user_id: Optional[int] = None,
        event_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_events_read)
):
    """
    Получение журнала событий с фильтрацией и пагинацией.

    - **page**: Номер страницы
    - **page_size**: Размер страницы
    - **user_id**: Фильтр по ID пользователя
    - **event_type**: Фильтр по типу события
    - **entity_type**: Фильтр по типу сущности
    - **start_date**: Фильтр по начальной дате
    - **end_date**: Фильтр по конечной дате
    """
    try:
        # Получаем события с применением фильтров
        events, total = await get_events(
            db=db,
            page=page,
            page_size=page_size,
            user_id=user_id,
            event_type=event_type,
            entity_type=entity_type,
            start_date=start_date,
            end_date=end_date
        )

        # Подготавливаем список событий для ответа
        event_items = []
        for event in events:
            # Получаем email пользователя (если есть)
            user_email = None
            if event.user_id:
                user = db.query(User).filter(User.id == event.user_id).first()
                if user:
                    user_email = user.email

            # Создаем элемент списка
            event_items.append(EventLogDetail(
                id=event.id,
                timestamp=event.timestamp,
                user_id=event.user_id,
                user_email=user_email,
                event_type=event.event_type,
                entity_type=event.entity_type,
                entity_id=event.entity_id,
                ip_address=event.ip_address,
                user_agent=event.user_agent,
                payload=event.payload
            ))

        # Формируем ответ с пагинацией
        return EventLogListResponse(
            items=event_items,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Error getting event log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения журнала событий: {str(e)}"
        )


@router.get("/{event_id}", response_model=EventLogDetail)
async def get_event_details(
        event_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_events_read)
):
    """
    Получение детальной информации о событии.

    - **event_id**: ID события
    """
    try:
        # Получаем событие по ID
        event = await get_event_by_id(db, event_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        # Получаем email пользователя (если есть)
        user_email = None
        if event.user_id:
            user = db.query(User).filter(User.id == event.user_id).first()
            if user:
                user_email = user.email

        # Формируем ответ
        return EventLogDetail(
            id=event.id,
            timestamp=event.timestamp,
            user_id=event.user_id,
            user_email=user_email,
            event_type=event.event_type,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            payload=event.payload
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения деталей события: {str(e)}"
        )


@router.get("/stats/summary", response_model=dict)
async def get_events_summary(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_events_read)
):
    """
    Получение статистики по типам событий.

    - **start_date**: Начальная дата для фильтрации статистики
    - **end_date**: Конечная дата для фильтрации статистики
    """
    try:
        # Получаем статистику по типам событий
        stats = await get_event_stats(db, start_date, end_date)

        return stats

    except Exception as e:
        logger.error(f"Error getting event stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики событий: {str(e)}"
        )
