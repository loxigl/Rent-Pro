from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import PyJWTError
import logging
import redis
import os
from fastapi import HTTPException, status

from src.schemas.admin import TokenData
from src.config.settings import settings

logger = logging.getLogger(__name__)

# Секретный ключ для подписи JWT токенов
# В продакшене должен храниться в переменных окружения
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey123")
ALGORITHM = "HS256"

# Время жизни токенов
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 минут
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 дней

# Подключение к Redis для хранения blacklist токенов
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=1,  # Используем отдельную DB для токенов
    decode_responses=True
)


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Создает JWT access token.

    Args:
        data: Данные для включения в токен

    Returns:
        str: Encoded JWT access token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Создает JWT refresh token.

    Args:
        data: Данные для включения в токен

    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Декодирует JWT токен.

    Args:
        token: JWT токен для декодирования

    Returns:
        Dict[str, Any]: Декодированные данные из токена

    Raises:
        HTTPException: Если токен невалидный или истек срок его действия
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except PyJWTError as e:
        logger.error(f"Error decoding token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительные учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_access_token(token: str) -> TokenData:
    """
    Проверяет JWT access token и возвращает данные пользователя.

    Args:
        token: JWT токен для проверки

    Returns:
        TokenData: Данные пользователя из токена

    Raises:
        HTTPException: Если токен невалидный, истек срок его действия или токен в blacklist
    """
    # Проверяем, находится ли токен в blacklist
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен отозван",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Декодируем токен
    payload = decode_token(token)

    # Проверяем наличие необходимых полей
    email: str = payload.get("sub")
    role: str = payload.get("role")
    user_id: int = payload.get("user_id")

    if email is None or role is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недостаточно данных в токене",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = TokenData(sub=email, role=role, user_id=user_id)
    return token_data


def verify_refresh_token(token: str) -> TokenData:
    """
    Проверяет JWT refresh token и возвращает данные пользователя.

    Args:
        token: JWT токен для проверки

    Returns:
        TokenData: Данные пользователя из токена

    Raises:
        HTTPException: Если токен невалидный, истек срок его действия или токен в blacklist
    """
    # Проверяем, находится ли токен в blacklist
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен отозван",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Декодируем токен
    payload = decode_token(token)

    # Проверяем наличие необходимых полей
    email: str = payload.get("sub")
    role: str = payload.get("role")
    user_id: int = payload.get("user_id")

    if email is None or role is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недостаточно данных в токене",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверяем, что это действительно refresh token
    token_type = payload.get("token_type")
    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный тип токена",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = TokenData(sub=email, role=role, user_id=user_id)
    return token_data


def add_token_to_blacklist(token: str, expires_delta: Optional[timedelta] = None) -> None:
    """
    Добавляет токен в blacklist.

    Args:
        token: JWT токен для добавления в blacklist
        expires_delta: Время жизни записи в Redis (по умолчанию = время жизни токена)
    """
    try:
        # Декодируем токен для получения времени истечения
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": True})
        exp = payload.get("exp")

        # Если не передано время жизни записи, используем время истечения токена
        if expires_delta is None and exp:
            expires_delta = datetime.fromtimestamp(exp) - datetime.utcnow()
        elif expires_delta is None:
            # Если не удалось получить время истечения, используем максимальное время жизни токена
            expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS + 1)

        # Добавляем токен в blacklist
        redis_client.set(f"blacklist:{token}", "1", ex=int(expires_delta.total_seconds()))
    except Exception as e:
        logger.error(f"Error adding token to blacklist: {e}")


def is_token_blacklisted(token: str) -> bool:
    """
    Проверяет, находится ли токен в blacklist.

    Args:
        token: JWT токен для проверки

    Returns:
        bool: True, если токен в blacklist, иначе False
    """
    try:
        return bool(redis_client.get(f"blacklist:{token}"))
    except Exception as e:
        logger.error(f"Error checking token in blacklist: {e}")
        return False


def create_tokens_for_user(user_id: int, email: str, role: str) -> tuple[str, str]:
    """
    Создает пару токенов (access и refresh) для пользователя.

    Args:
        user_id: ID пользователя
        email: Email пользователя
        role: Роль пользователя

    Returns:
        tuple[str, str]: (access_token, refresh_token)
    """
    # Данные для access token
    access_data = {
        "sub": email,
        "role": role,
        "user_id": user_id,
        "token_type": "access"
    }

    # Данные для refresh token
    refresh_data = {
        "sub": email,
        "role": role,
        "user_id": user_id,
        "token_type": "refresh"
    }

    # Создаем токены
    access_token = create_access_token(data=access_data)
    refresh_token = create_refresh_token(data=refresh_data)

    return access_token, refresh_token
