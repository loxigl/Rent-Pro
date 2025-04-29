from sqlalchemy import Column, String, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.sql import func
import logging

from src.db.database import Base

logger = logging.getLogger(__name__)


class RolePermission(Base):
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
OWNER_PERMISSIONS = [
    "apartments:read",
    "apartments:write",
    "photos:read",
    "photos:write",
    "events:read",
    "users:read",
    "users:write",
]

MANAGER_PERMISSIONS = [
    "apartments:read",
    "apartments:write",
    "photos:read",
    "photos:write",
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
        for role_perm in db_session.query(RolePermission).all():
            if role_perm.role not in existing_permissions:
                existing_permissions[role_perm.role] = set()
            existing_permissions[role_perm.role].add(role_perm.perm)

        # Счетчик добавленных разрешений
        added_count = 0

        # Добавляем недостающие разрешения для владельца
        for perm in OWNER_PERMISSIONS:
            if "owner" not in existing_permissions or perm not in existing_permissions["owner"]:
                db_session.add(RolePermission(role="owner", perm=perm))
                added_count += 1

        # Добавляем недостающие разрешения для менеджера
        for perm in MANAGER_PERMISSIONS:
            if "manager" not in existing_permissions or perm not in existing_permissions["manager"]:
                db_session.add(RolePermission(role="manager", perm=perm))
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
