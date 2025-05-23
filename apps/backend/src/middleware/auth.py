from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging

from src.db.database import get_db
from src.models import RolePermission
from src.services.auth import verify_access_token
from src.schemas.admin import TokenData
from src.models.auth import User

logger = logging.getLogger(__name__)

# Настройка OAuth2 для получения токена из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/api/v1/auth/login")

# Определение разрешений для защищенных ресурсов
MANAGE_APARTMENTS = ["apartments:write"]
MANAGE_PHOTOS = ["photos:write"]
VIEW_EVENTS = ["events:read"]
MANAGE_USERS = ["users:write"]
MANAGE_BOOKINGS = ["bookings:write"]
MANAGE_SETTINGS = ["settings:write"]


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    """
    Получает текущего пользователя на основе JWT-токена.

    Args:
        token: JWT-токен из заголовка Authorization
        db: Сессия базы данных

    Returns:
        User: Объект текущего пользователя

    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    # Проверяем токен и получаем данные пользователя
    token_data = verify_access_token(token)

    # Получаем пользователя из базы данных
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        logger.warning(f"User with ID {token_data.user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверяем, что пользователь активен
    if not user.is_active:
        logger.warning(f"User with ID {token_data.user_id} is inactive")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт отключен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Проверяет, что текущий пользователь активен.

    Args:
        current_user: Текущий пользователь

    Returns:
        User: Текущий активный пользователь

    Raises:
        HTTPException: Если пользователь неактивен
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт отключен",
        )
    return current_user


def get_owner_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Проверяет, что текущий пользователь имеет роль владельца.

    Args:
        current_user: Текущий пользователь

    Returns:
        User: Текущий пользователь с ролью владельца

    Raises:
        HTTPException: Если пользователь не владелец
    """
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права владельца",
        )
    return current_user


def get_manager_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Проверяет, что текущий пользователь имеет роль менеджера или владельца.

    Args:
        current_user: Текущий пользователь

    Returns:
        User: Текущий пользователь с ролью менеджера или владельца

    Raises:
        HTTPException: Если пользователь не менеджер и не владелец
    """
    if current_user.role not in ["manager", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права менеджера",
        )
    return current_user


def check_permissions(required_permissions=None):
    """
    Создает зависимость для проверки разрешений пользователя.

    Args:
        required_permissions: Список или одиночное разрешение, необходимое для доступа

    Returns:
        Функция зависимости, которая возвращает пользователя, если у него есть необходимые разрешения
    """

    async def _check_user_permissions(current_user: User = Depends(get_current_active_user)) -> User:
        # Если разрешения не указаны, просто возвращаем пользователя
        if not required_permissions:
            return current_user

        # Получаем список разрешений пользователя
        user_permissions = []
        if current_user.role == "owner":
            # Владелец имеет все разрешения
            user_permissions = [perm.value for perm in RolePermission]
        elif current_user.permissions:
            # Используем сохраненные разрешения пользователя
            user_permissions = current_user.permissions

        # Проверяем наличие требуемых разрешений
        if isinstance(required_permissions, list):
            # Если требуется несколько разрешений
            if not all(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для выполнения операции",
                )
        else:
            # Если требуется одно разрешение
            if required_permissions not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для выполнения операции",
                )

        return current_user

    return _check_user_permissions
