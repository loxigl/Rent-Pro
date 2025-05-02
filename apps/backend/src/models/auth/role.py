from enum import Enum, auto
from sqlalchemy import Column, String, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.sql import func
import logging

from src.db.database import Base

logger = logging.getLogger(__name__)


class RolePermission(str, Enum):
    """
    Перечисление всех возможных разрешений в системе.
    Используется для проверки прав доступа в декораторах.
    """
    # Квартиры
    APARTMENTS_READ = "apartments:read"
    APARTMENTS_WRITE = "apartments:write"
    MANAGE_APARTMENTS = "apartments:write"  # Алиас для обратной совместимости

    # Фотографии
    PHOTOS_READ = "photos:read"
    PHOTOS_WRITE = "photos:write"
    MANAGE_PHOTOS = "photos:write"  # Алиас для обратной совместимости

    # Журнал событий
    EVENTS_READ = "events:read"
    VIEW_EVENTS = "events:read"  # Алиас для обратной совместимости

    # Пользователи
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    MANAGE_USERS = "users:write"  # Алиас для обратной совместимости

    # Бронирования
    BOOKINGS_READ = "bookings:read"
    BOOKINGS_WRITE = "bookings:write"
    MANAGE_BOOKINGS = "bookings:write"  # Алиас для обратной совместимости

    # Настройки
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"
    MANAGE_SETTINGS = "settings:write"  # Алиас для обратной совместимости


class RolePermissionModel(Base):
    """
    Модель разрешений для ролей в системе.
    Каждая запись связывает роль с определённым разрешением.

    Роли:
    - owner: владелец системы, имеет все разрешения
    - manager: менеджер, управляет квартирами и фотографиями

    Разрешения (perm):
    - apartments:read - просмотр списка квартир
    - apartments:write - создание/редактирование квартир
    - photos:read - просмотр фотографий
    - photos:write - загрузка/редактирование фотографий
    - events:read - просмотр журнала событий
    - users:read - просмотр пользователей
    - users:write - создание/редактирование пользователей
    - bookings:read - просмотр бронирований
    - bookings:write - управление бронированиями
    - settings:read - просмотр настроек системы
    - settings:write - изменение настроек системы
    """
    __tablename__ = "role_permissions"

    role = Column(String(10), nullable=False)
    perm = Column(String(40), nullable=False)

    # Первичный ключ - комбинация роли и разрешения
    __table_args__ = (
        PrimaryKeyConstraint('role', 'perm', name='pk_role_perm'),
        CheckConstraint(
            "role IN ('owner', 'manager')",
            name='check_valid_role_perm'
        ),
    )

    def __repr__(self):
        return f"<RolePermission role={self.role} perm={self.perm}>"


# Предопределенные разрешения для ролей
OWNER_PERMISSIONS = [perm.value for perm in RolePermission if not perm.value.endswith("_ALIAS")]
MANAGER_PERMISSIONS = [
    RolePermission.APARTMENTS_READ.value,
    RolePermission.APARTMENTS_WRITE.value,
    RolePermission.PHOTOS_READ.value,
    RolePermission.PHOTOS_WRITE.value,
    RolePermission.BOOKINGS_READ.value,
    RolePermission.BOOKINGS_WRITE.value,
]


# Улучшенная функция инициализации разрешений
def initialize_permissions(db_session):
    """
    Инициализирует разрешения для ролей в базе данных.
    Добавляет только недостающие разрешения, не удаляя существующие.

    Args:
        db_session: Сессия базы данных SQLAlchemy
    """
    try:
        # Получаем существующие разрешения
        existing_permissions = {}
        for role_perm in db_session.query(RolePermissionModel).all():
            if role_perm.role not in existing_permissions:
                existing_permissions[role_perm.role] = set()
            existing_permissions[role_perm.role].add(role_perm.perm)

        # Счетчик добавленных разрешений
        added_count = 0

        # Добавляем недостающие разрешения для владельца
        for perm in OWNER_PERMISSIONS:
            if "owner" not in existing_permissions or perm not in existing_permissions["owner"]:
                db_session.add(RolePermissionModel(role="owner", perm=perm))
                added_count += 1

        # Добавляем недостающие разрешения для менеджера
        for perm in MANAGER_PERMISSIONS:
            if "manager" not in existing_permissions or perm not in existing_permissions["manager"]:
                db_session.add(RolePermissionModel(role="manager", perm=perm))
                added_count += 1

        if added_count > 0:
            db_session.commit()
            logger.info(f"Добавлено {added_count} недостающих разрешений")
        else:
            logger.info("Все необходимые разрешения уже существуют")

        return True
    except Exception as e:
        db_session.rollback()
        logger.error(f"Ошибка при инициализации разрешений: {e}")
        return False
