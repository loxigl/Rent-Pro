from sqlalchemy import Column, Integer, String, DateTime, Boolean, CheckConstraint
from sqlalchemy.sql import func

from src.db.database import Base


class User(Base):
    """
    Модель пользователя для админ-панели.
    Содержит информацию о пользователях, которые могут управлять квартирами.
    Роли: 'owner' - владелец системы, 'manager' - менеджер квартир
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    # Роль пользователя: 'owner' или 'manager'
    role = Column(String(10), nullable=False)

    # Check constraint для проверки валидных ролей
    __table_args__ = (
        CheckConstraint(
            "role IN ('owner', 'manager')",
            name='check_valid_role'
        ),
    )

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"
