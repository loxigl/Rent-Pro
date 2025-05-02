from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from src.db.database import get_db
from src.models.auth import User
from src.models.event_log import EventType, EntityType
from src.schemas.admin import LoginRequest, Token, RefreshTokenRequest, ChangePasswordRequest
from src.services.auth import (
    verify_password, create_tokens_for_user, verify_refresh_token,
    add_token_to_blacklist
)
from src.middleware.auth import get_current_active_user
from src.services.event_log_service import log_event
from src.models.event_log import EntityType, EventType

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=Token)
async def login(
        request: Request,
        auth_data: LoginRequest,
        db: Session = Depends(get_db)
):
    """
    Вход в систему администратора.

    - **email**: Email пользователя
    - **password**: Пароль пользователя

    Возвращает пару JWT-токенов (access и refresh).
    """
    # Ищем пользователя по email
    user = db.query(User).filter(User.email == auth_data.email).first()

    # Проверяем, что пользователь существует и пароль верный
    if not user or not verify_password(auth_data.password, user.password_hash):
        logger.warning(f"Failed login attempt for email: {auth_data.email}")
        # Логируем событие неудачной авторизации
        await log_event(
            db=db,
            event_type=EventType.USER_LOGIN,
            entity_type=EntityType.USER,
            payload={"status": "failed", "email": auth_data.email},
            request=request
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверяем, что пользователь активен
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {auth_data.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт отключен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Создаем токены
    access_token, refresh_token = create_tokens_for_user(
        user_id=user.id,
        email=user.email,
        role=user.role
    )

    # Обновляем информацию о последнем входе
    user.last_login = datetime.now()
    db.commit()

    # Логируем событие успешной авторизации
    await log_event(
        db=db,
        event_type=EventType.USER_LOGIN,
        user_id=user.id,
        entity_type=EntityType.USER,
        entity_id=str(user.id),
        payload={"status": "success"},
        request=request
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
        refresh_data: RefreshTokenRequest,
        db: Session = Depends(get_db)
):
    """
    Обновление токена доступа с использованием refresh-токена.

    - **refresh_token**: Refresh-токен

    Возвращает новую пару JWT-токенов (access и refresh).
    """
    try:
        # Проверяем refresh-токен
        token_data = verify_refresh_token(refresh_data.refresh_token)

        # Ищем пользователя по данным из токена
        user = db.query(User).filter(User.id == token_data.user_id).first()

        if not user or not user.is_active:
            # Добавляем токен в черный список
            add_token_to_blacklist(refresh_data.refresh_token)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден или неактивен",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Создаем новые токены
        access_token, refresh_token = create_tokens_for_user(
            user_id=user.id,
            email=user.email,
            role=user.role
        )

        # Добавляем старый refresh-токен в черный список
        add_token_to_blacklist(refresh_data.refresh_token)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except HTTPException:
        # Пробрасываем исключение дальше
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh-токен",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
        request: Request,
        refresh_data: RefreshTokenRequest,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Выход из системы администратора.

    - **refresh_token**: Refresh-токен

    Добавляет токены в черный список.
    """
    try:
        # Добавляем refresh-токен в черный список
        add_token_to_blacklist(refresh_data.refresh_token)

        # Логируем событие выхода
        await log_event(
            db=db,
            event_type=EventType.USER_LOGOUT,
            user_id=current_user.id,
            entity_type=EntityType.USER,
            entity_id=str(current_user.id),
            request=request
        )

        return None

    except Exception as e:
        logger.error(f"Error during logout: {e}")
        # Даже в случае ошибки возвращаем 204, так как цель - выход пользователя
        return None


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
        request: Request,
        password_data: ChangePasswordRequest,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Изменение пароля пользователя.

    - **current_password**: Текущий пароль
    - **new_password**: Новый пароль
    """
    # Проверяем текущий пароль
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль",
        )

    # Обновляем пароль
    from src.services.auth import hash_password
    current_user.password_hash = hash_password(password_data.new_password)

    # Сохраняем изменения в БД
    db.commit()

    # Логируем событие изменения пароля
    await log_event(
        db=db,
        event_type="password_changed",
        user_id=current_user.id,
        entity_type=EntityType.USER,
        entity_id=str(current_user.id),
        request=request
    )

    return {"message": "Пароль успешно изменен"}
