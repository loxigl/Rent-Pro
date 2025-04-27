import uuid
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.db.database import Base


class EventLog(Base):
    """
    Модель для журнала событий в системе.
    Используется для отслеживания действий пользователей в админ-панели.

    Типы событий (event_type):
    - user_login - вход пользователя
    - user_logout - выход пользователя
    - apartment_created - создание квартиры
    - apartment_updated - изменение квартиры
    - apartment_deleted - удаление квартиры
    - photo_uploaded - загрузка фотографии
    - photo_deleted - удаление фотографии
    - photo_updated - изменение порядка/обложки фотографии
    """
    __tablename__ = "event_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=True)  # apartment, photo, user
    entity_id = Column(String(50), nullable=True)  # ID связанной сущности
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)

    # Дополнительные данные о событии в формате JSON
    payload = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<EventLog id={self.id} type={self.event_type} user_id={self.user_id}>"


# Константы для типов событий
class EventType:
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    APARTMENT_CREATED = "apartment_created"
    APARTMENT_UPDATED = "apartment_updated"
    APARTMENT_DELETED = "apartment_deleted"
    PHOTO_UPLOADED = "photo_uploaded"
    PHOTO_DELETED = "photo_deleted"
    PHOTO_UPDATED = "photo_updated"


# Константы для типов сущностей
class EntityType:
    APARTMENT = "apartment"
    PHOTO = "photo"
    USER = "user"
