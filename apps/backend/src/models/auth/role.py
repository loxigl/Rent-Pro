from sqlalchemy import Column, String, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.sql import func

from src.db.database import Base


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


# Функция для инициализации разрешений в базе данных
def initialize_permissions(db_session):
    """
    Инициализирует разрешения для ролей в базе данных.
    Должна вызываться при миграции или первом запуске приложения.

    Args:
        db_session: Сессия базы данных SQLAlchemy
    """
    # Сначала удаляем все существующие разрешения
    db_session.query(RolePermission).delete()

    # Добавляем разрешения для владельца
    for perm in OWNER_PERMISSIONS:
        db_session.add(RolePermission(role="owner", perm=perm))

    # Добавляем разрешения для менеджера
    for perm in MANAGER_PERMISSIONS:
        db_session.add(RolePermission(role="manager", perm=perm))

    db_session.commit()
