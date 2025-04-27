from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from src.models.auth import RolePermission, OWNER_PERMISSIONS, MANAGER_PERMISSIONS

logger = logging.getLogger(__name__)


def get_user_permissions(db: Session, role: str) -> List[str]:
    """
    Получает список разрешений для роли из базы данных.

    Args:
        db: Сессия базы данных
        role: Роль пользователя (owner, manager)

    Returns:
        List[str]: Список разрешений для роли
    """
    try:
        if role not in ['owner', 'manager']:
            return []

        permissions = db.query(RolePermission.perm).filter(RolePermission.role == role).all()
        return [perm[0] for perm in permissions]
    except Exception as e:
        logger.error(f"Error getting permissions for role {role}: {e}")
        # В случае ошибки возвращаем предопределенные разрешения из памяти
        if role == 'owner':
            return OWNER_PERMISSIONS
        elif role == 'manager':
            return MANAGER_PERMISSIONS
        return []


def has_permission(db: Session, role: str, required_permission: str) -> bool:
    """
    Проверяет, имеет ли роль указанное разрешение.

    Args:
        db: Сессия базы данных
        role: Роль пользователя (owner, manager)
        required_permission: Требуемое разрешение

    Returns:
        bool: True, если роль имеет разрешение, иначе False
    """
    # Получаем разрешения пользователя
    permissions = get_user_permissions(db, role)

    # Проверяем наличие разрешения
    return required_permission in permissions


def check_permissions(db: Session, role: str, required_permissions: List[str]) -> bool:
    """
    Проверяет, имеет ли роль все указанные разрешения.

    Args:
        db: Сессия базы данных
        role: Роль пользователя (owner, manager)
        required_permissions: Список требуемых разрешений

    Returns:
        bool: True, если роль имеет все разрешения, иначе False
    """
    # Получаем разрешения пользователя
    permissions = get_user_permissions(db, role)

    # Проверяем наличие всех разрешений
    return all(perm in permissions for perm in required_permissions)


def check_any_permission(db: Session, role: str, required_permissions: List[str]) -> bool:
    """
    Проверяет, имеет ли роль хотя бы одно из указанных разрешений.

    Args:
        db: Сессия базы данных
        role: Роль пользователя (owner, manager)
        required_permissions: Список требуемых разрешений

    Returns:
        bool: True, если роль имеет хотя бы одно разрешение, иначе False
    """
    # Получаем разрешения пользователя
    permissions = get_user_permissions(db, role)

    # Проверяем наличие хотя бы одного разрешения
    return any(perm in permissions for perm in required_permissions)


def load_permissions_to_cache(db: Session) -> dict:
    """
    Загружает все разрешения из БД в кеш.
    Используется при запуске приложения для ускорения проверки разрешений.

    Args:
        db: Сессия базы данных

    Returns:
        dict: Словарь {role: [permissions]}
    """
    try:
        # Получаем все разрешения из БД
        role_permissions = db.query(RolePermission).all()

        # Формируем словарь {role: [permissions]}
        permissions_cache = {}
        for rp in role_permissions:
            if rp.role not in permissions_cache:
                permissions_cache[rp.role] = []
            permissions_cache[rp.role].append(rp.perm)

        return permissions_cache
    except Exception as e:
        logger.error(f"Error loading permissions to cache: {e}")
        # В случае ошибки возвращаем предопределенные разрешения из памяти
        return {
            'owner': OWNER_PERMISSIONS,
            'manager': MANAGER_PERMISSIONS
        }
