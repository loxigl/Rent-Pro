import bcrypt
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Создает хеш пароля с использованием bcrypt.

    Args:
        password: Пароль в открытом виде

    Returns:
        str: Хеш пароля
    """
    # Генерация соли и хеширование пароля
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли пароль хешу.

    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Хеш пароля

    Returns:
        bool: True, если пароль соответствует хешу, иначе False
    """
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def validate_password(password: str) -> tuple[bool, str]:
    """
    Проверяет, соответствует ли пароль требованиям безопасности.

    Args:
        password: Пароль для проверки

    Returns:
        tuple[bool, str]: (True, "") если пароль корректен, иначе (False, причина)
    """
    # Проверка минимальной длины
    if len(password) < 6:
        return False, "Пароль должен содержать не менее 6 символов"

    # Дополнительные проверки безопасности могут быть добавлены здесь
    # Например, наличие букв разного регистра, цифр, специальных символов и т.д.

    return True, ""
