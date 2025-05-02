from datetime import datetime
from typing import Optional, Union, Dict, Any, List
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from sqlalchemy.orm import selectinload
from src.db.database import get_db
from fastapi import Request
from src.models.event_log import EventLog, EventType, EntityType


def log_action(
        db: Session,
        entity_type: EntityType,
        entity_id: Union[int, str],
        event_type: EventType,
        description: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
):
    """
    Записывает событие в журнал действий.

    Args:
        db: Сессия базы данных
        entity_type: Тип сущности (APARTMENT, USER, BOOKING и т.д.)
        entity_id: ID сущности
        event_type: Тип события (CREATE, UPDATE, DELETE и т.д.)
        description: Описание события
        user_id: ID пользователя, выполнившего действие (опционально)
        metadata: Дополнительные данные, связанные с событием (опционально)
    """
    try:
        event = EventLog(
            entity_type=entity_type,
            entity_id=str(entity_id),
            event_type=event_type,
            description=description,
            user_id=user_id,
            metadata=metadata
        )

        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    except Exception as e:
        db.rollback()
        raise e


def get_events(
        db: Session,
        entity_type: Optional[EntityType] = None,
        entity_id: Optional[str] = None,
        event_type: Optional[EventType] = None,
        user_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
) -> tuple[List[EventLog], int]:
    """
    Получает записи журнала событий с возможностью фильтрации.

    Args:
        db: Сессия базы данных
        entity_type: Фильтр по типу сущности
        entity_id: Фильтр по ID сущности
        event_type: Фильтр по типу события
        user_id: Фильтр по ID пользователя
        limit: Максимальное количество записей
        offset: Смещение для пагинации

    Returns:
        Кортеж (список событий, общее количество записей)
    """
    query = select(EventLog).order_by(desc(EventLog.timestamp))
    count_query = select(func.count()).select_from(EventLog)

    # Применяем фильтры, если они указаны
    if entity_type:
        query = query.where(EventLog.entity_type == entity_type)
        count_query = count_query.where(EventLog.entity_type == entity_type)

    if entity_id:
        query = query.where(EventLog.entity_id == str(entity_id))
        count_query = count_query.where(EventLog.entity_id == str(entity_id))

    if event_type:
        query = query.where(EventLog.event_type == event_type)
        count_query = count_query.where(EventLog.event_type == event_type)

    if user_id:
        query = query.where(EventLog.user_id == user_id)
        count_query = count_query.where(EventLog.user_id == user_id)

    # Применяем пагинацию
    query = query.offset(offset).limit(limit)

    # Выполняем запросы
    result = db.execute(query)
    count_result = db.execute(count_query)

    # Получаем результаты
    events = result.scalars().all()
    total_count = count_result.scalar_one()

    return events, total_count


def get_event_by_id(db: Session, event_id: int) -> Optional[EventLog]:
    """
    Получает событие по его ID.

    Args:
        db: Сессия базы данных
        event_id: ID события

    Returns:
        Объект события или None, если событие не найдено
    """
    query = select(EventLog).where(EventLog.id == event_id)
    result = db.execute(query)
    return result.scalar_one_or_none()


def log_event(
        db: Session,
        event_type: EventType,
        entity_type: EntityType,
        entity_id: str = None,
        user_id: int = None,
        payload: dict = None,
        request: Request = None
):
    """
    Логирует событие в журнал действий.

    Args:
        db: Сессия базы данных
        event_type: Тип события
        entity_type: Тип сущности
        entity_id: ID сущности (опционально)
        user_id: ID пользователя (опционально)
        payload: Дополнительные данные события (опционально)
        request: Объект запроса (опционально)
    """
    # Получаем IP и User-Agent из запроса, если он предоставлен
    metadata = {}
    if request:
        client_host = request.client.host if hasattr(request, 'client') else None
        metadata.update({
            "ip_address": client_host,
            "user_agent": request.headers.get("user-agent")
        })

    if payload:
        metadata.update({"payload": payload})

    # Вызываем функцию log_action для фактического сохранения
    return log_action(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id or "system",
        event_type=event_type,
        description=(
            f"{event_type.value if hasattr(event_type, 'value') else event_type} "
            f"для {entity_type.value if hasattr(entity_type, 'value') else entity_type}"
        ),
        user_id=user_id,
        metadata=metadata
    )


def get_event_stats(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> dict:
    """
    Получает статистику по типам событий с возможностью фильтрации по датам.

    Args:
        db: Сессия базы данных
        start_date: Начальная дата для фильтрации
        end_date: Конечная дата для фильтрации

    Returns:
        Словарь со статистикой по типам событий и сущностей
    """
    # Базовый запрос для статистики по типам событий
    event_type_query = select(
        EventLog.event_type,
        func.count(EventLog.id).label('count')
    ).group_by(EventLog.event_type)

    # Базовый запрос для статистики по типам сущностей
    entity_type_query = select(
        EventLog.entity_type,
        func.count(EventLog.id).label('count')
    ).group_by(EventLog.entity_type)

    # Базовый запрос для статистики по пользователям
    user_query = select(
        EventLog.user_id,
        func.count(EventLog.id).label('count')
    ).where(EventLog.user_id.isnot(None)).group_by(EventLog.user_id)

    # Применяем фильтры по датам, если они указаны
    if start_date:
        event_type_query = event_type_query.where(EventLog.timestamp >= start_date)
        entity_type_query = entity_type_query.where(EventLog.timestamp >= start_date)
        user_query = user_query.where(EventLog.timestamp >= start_date)

    if end_date:
        event_type_query = event_type_query.where(EventLog.timestamp <= end_date)
        entity_type_query = entity_type_query.where(EventLog.timestamp <= end_date)
        user_query = user_query.where(EventLog.timestamp <= end_date)

    # Запрос на общее количество событий
    total_query = select(func.count(EventLog.id))
    if start_date:
        total_query = total_query.where(EventLog.timestamp >= start_date)
    if end_date:
        total_query = total_query.where(EventLog.timestamp <= end_date)

    # Выполняем запросы
    event_type_result = db.execute(event_type_query)
    entity_type_result = db.execute(entity_type_query)
    user_result = db.execute(user_query)
    total_result = db.execute(total_query)

    # Обрабатываем результат для типов событий
    event_type_stats = {}
    for event_type, count in event_type_result:
        event_type_stats[event_type.value] = count

    # Обрабатываем результат для типов сущностей
    entity_type_stats = {}
    for entity_type, count in entity_type_result:
        entity_type_stats[entity_type.value] = count

    # Обрабатываем результат для пользователей
    user_stats = []
    for user_id, count in user_result:
        user_stats.append({"user_id": user_id, "count": count})

    # Сортируем пользователей по количеству событий (в порядке убывания)
    user_stats.sort(key=lambda x: x["count"], reverse=True)

    # Получаем общее количество событий
    total_count = total_result.scalar_one() or 0

    # Формируем результат
    return {
        "total_events": total_count,
        "by_event_type": event_type_stats,
        "by_entity_type": entity_type_stats,
        "by_user": user_stats[:10],  # Ограничиваем список топ-10 пользователей
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    }
