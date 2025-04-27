from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Callable
import logging
from functools import wraps

from src.db.database import get_db
from src.middleware.auth import get_current_active_user
from src.models.auth import User
from src.services.auth import has_permission, check_permissions, check_any_permission

logger = logging.getLogger(__name__)


def require_permission(permission: str):
    """
    Декоратор для проверки наличия разрешения у пользователя.

    Args:
        permission: Требуемое разрешение

    Returns:
        User: Текущий пользователь, если у него есть разрешение

    Raises:
        HTTPException: Если у пользователя нет разрешения
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db),
                          **kwargs):
            if not has_permission(db, current_user.role, permission):
                logger.warning(f"User {current_user.id} ({current_user.email}) does not have permission: {permission}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Требуется разрешение: {permission}",
                )
            return await func(*args, current_user=current_user, db=db, **kwargs)

        return wrapper

    return decorator


def require_permissions(permissions: List[str]):
    """
    Декоратор для проверки наличия всех указанных разрешений у пользователя.

    Args:
        permissions: Список требуемых разрешений

    Returns:
        User: Текущий пользователь, если у него есть все разрешения

    Raises:
        HTTPException: Если у пользователя нет хотя бы одного разрешения
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db),
                          **kwargs):
            if not check_permissions(db, current_user.role, permissions):
                logger.warning(
                    f"User {current_user.id} ({current_user.email}) does not have all required permissions: {permissions}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Требуются разрешения: {', '.join(permissions)}",
                )
            return await func(*args, current_user=current_user, db=db, **kwargs)

        return wrapper

    return decorator


def require_any_permission(permissions: List[str]):
    """
    Декоратор для проверки наличия хотя бы одного из указанных разрешений у пользователя.

    Args:
        permissions: Список разрешений, из которых требуется хотя бы одно

    Returns:
        User: Текущий пользователь, если у него есть хотя бы одно разрешение

    Raises:
        HTTPException: Если у пользователя нет ни одного из разрешений
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db),
                          **kwargs):
            if not check_any_permission(db, current_user.role, permissions):
                logger.warning(
                    f"User {current_user.id} ({current_user.email}) does not have any of the required permissions: {permissions}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Требуется хотя бы одно из разрешений: {', '.join(permissions)}",
                )
            return await func(*args, current_user=current_user, db=db, **kwargs)

        return wrapper

    return decorator


# Предопределенные зависимости для часто используемых разрешений

def require_apartments_read(current_user: User = Depends(get_current_active_user),
                            db: Session = Depends(get_db)) -> User:
    """Проверяет наличие разрешения на чтение квартир."""
    if not has_permission(db, current_user.role, "apartments:read"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется разрешение: apartments:read")
    return current_user


def require_apartments_write(current_user: User = Depends(get_current_active_user),
                             db: Session = Depends(get_db)) -> User:
    """Проверяет наличие разрешения на запись квартир."""
    if not has_permission(db, current_user.role, "apartments:write"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется разрешение: apartments:write")
    return current_user


def require_photos_read(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)) -> User:
    """Проверяет наличие разрешения на чтение фотографий."""
    if not has_permission(db, current_user.role, "photos:read"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется разрешение: photos:read")
    return current_user


def require_photos_write(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)) -> User:
    """Проверяет наличие разрешения на запись фотографий."""
    if not has_permission(db, current_user.role, "photos:write"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется разрешение: photos:write")
    return current_user


def require_events_read(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)) -> User:
    """Проверяет наличие разрешения на чтение журнала событий."""
    if not has_permission(db, current_user.role, "events:read"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется разрешение: events:read")
    return current_user


def require_users_read(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)) -> User:
    """Проверяет наличие разрешения на чтение пользователей."""
    if not has_permission(db, current_user.role, "users:read"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется разрешение: users:read")
    return current_user


def require_users_write(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)) -> User:
    """Проверяет наличие разрешения на запись пользователей."""
    if not has_permission(db, current_user.role, "users:write"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется разрешение: users:write")
    return current_user
