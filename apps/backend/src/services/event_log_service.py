from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import Request

from src.models.event_log import EventLog, EventType, EntityType


async def log_event(
        db: Session,
        event_type: str,
        user_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
) -> EventLog:
    """
    Записывает событие в журнал.

    Args:
        db: Сессия базы данных
        event_type: Тип события (из EventType)
        user_id: ID пользователя, совершившего действие
        entity_type: Тип сущности (из EntityType)
        entity_id: ID сущности
        payload: Дополнительные данные о событии
        request: Объект запроса FastAPI (для получения IP и User-Agent)

    Returns:
        EventLog: Созданная запись о событии
    """
    # Получаем IP-адрес и User-Agent из запроса, если он передан
    ip_address = None
    user_agent = None

    if request:
        # Получаем IP-адрес, учитывая возможность использования прокси
        ip_address = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Используем первый IP-адрес из списка X-Forwarded-For
            ip_address = forwarded_for.split(",")[0].strip()

        # Получаем User-Agent
        user_agent = request.headers.get("User-Agent")

    # Создаем запись о событии
    event_log = EventLog(
        user_id=user_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        ip_address=ip_address,
        user_agent=user_agent,
        payload=payload
    )

    # Сохраняем запись в базе данных
    db.add(event_log)
    db.commit()
    db.refresh(event_log)

    return event_log


async def get_events(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None,
        event_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
) -> tuple[List[EventLog], int]:
    """
    Получает список событий с фильтрацией и пагинацией.

    Args:
        db: Сессия базы данных
        page: Номер страницы
        page_size: Размер страницы
        user_id: Фильтр по ID пользователя
        event_type: Фильтр по типу события
        entity_type: Фильтр по типу сущности
        start_date: Фильтр по дате начала
        end_date: Фильтр по дате окончания

    Returns:
        tuple[List[EventLog], int]: Список событий и общее количество
    """
    # Формируем запрос с учетом фильтров
    query = db.query(EventLog)

    if user_id is not None:
        query = query.filter(EventLog.user_id == user_id)

    if event_type:
        query = query.filter(EventLog.event_type == event_type)

    if entity_type:
        query = query.filter(EventLog.entity_type == entity_type)

    if start_date:
        query = query.filter(EventLog.timestamp >= start_date)

    if end_date:
        query = query.filter(EventLog.timestamp <= end_date)

    # Получаем общее количество записей
    total = query.count()

    # Применяем пагинацию и сортировку
    events = query.order_by(desc(EventLog.timestamp)).offset((page - 1) * page_size).limit(page_size).all()

    return events, total


async def get_event_by_id(db: Session, event_id: str) -> Optional[EventLog]:
    """
    Получает событие по ID.

    Args:
        db: Сессия базы данных
        event_id: ID события

    Returns:
        Optional[EventLog]: Событие или None, если не найдено
    """
    return db.query(EventLog).filter(EventLog.id == event_id).first()


async def get_event_stats(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
) -> Dict[str, int]:
    """
    Получает статистику по типам событий.

    Args:
        db: Сессия базы данных
        start_date: Фильтр по дате начала
        end_date: Фильтр по дате окончания

    Returns:
        Dict[str, int]: Словарь {тип_события: количество}
    """
    # Формируем запрос с учетом фильтров
    query = db.query(EventLog.event_type, func.count(EventLog.id).label('count')).group_by(EventLog.event_type)

    if start_date:
        query = query.filter(EventLog.timestamp >= start_date)

    if end_date:
        query = query.filter(EventLog.timestamp <= end_date)

    # Выполняем запрос
    results = query.all()

    # Формируем словарь с результатами
    stats = {event_type: count for event_type, count in results}

    return stats