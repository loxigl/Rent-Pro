import logging
from typing import Optional, Union, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.event_log import EventLog, EntityType, EventType

logger = logging.getLogger("app.events")

async def log_action(
    db: AsyncSession,
    entity_type: EntityType,
    entity_id: Union[int, str],
    event_type: EventType,
    description: str,
    user_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Логирует действие в таблицу event_log.
    
    Args:
        db: Сессия базы данных
        entity_type: Тип сущности
        entity_id: ID сущности
        event_type: Тип события
        description: Описание события
        user_id: ID пользователя, совершившего действие (опционально)
        metadata: Дополнительные метаданные (опционально)
    """
    try:
        # Создаем запись в журнале событий
        event_log = EventLog(
            entity_type=entity_type,
            entity_id=str(entity_id),
            event_type=event_type,
            description=description,
            user_id=user_id,
            metadata=metadata
        )
        
        db.add(event_log)
        await db.commit()
        
        logger.info(
            f"Event logged: {event_type.value} for {entity_type.value} (ID: {entity_id})"
        )
    except Exception as e:
        logger.error(f"Error logging event: {str(e)}")
        await db.rollback()
        raise 