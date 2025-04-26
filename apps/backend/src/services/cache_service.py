import json
import logging
import redis
from typing import Any, Optional
import pickle

from src.config.settings import settings
from src.config.redis_settings import (
    CACHE_EXPIRATION,
    get_apartments_list_cache_key,
    get_apartment_detail_cache_key,
    get_apartment_photos_cache_key
)

logger = logging.getLogger(__name__)


class CacheService:
    """
    Сервис для работы с кешем Redis.
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=False
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Получение значения из кеша.

        Args:
            key: Ключ

        Returns:
            Any: Значение или None
        """
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting value from cache: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """
        Установка значения в кеш.

        Args:
            key: Ключ
            value: Значение
            expire: Время жизни в секундах (по умолчанию 5 минут)

        Returns:
            bool: Успешно или нет
        """
        try:
            serialized_value = pickle.dumps(value)
            return self.redis_client.set(key, serialized_value, ex=expire)
        except Exception as e:
            logger.error(f"Error setting value to cache: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Удаление значения из кеша.

        Args:
            key: Ключ

        Returns:
            bool: Успешно или нет
        """
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting value from cache: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Удаление всех ключей, соответствующих шаблону.

        Args:
            pattern: Шаблон ключей

        Returns:
            int: Количество удаленных ключей
        """
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing keys by pattern: {e}")
            return 0

    def get_apartments_cache_key(self, page: int, page_size: int, sort: str, order: str) -> str:
        """
        Генерация ключа кеша для списка квартир.

        Args:
            page: Номер страницы
            page_size: Размер страницы
            sort: Поле сортировки
            order: Порядок сортировки

        Returns:
            str: Ключ кеша
        """
        return get_apartments_list_cache_key(page, page_size, sort, order)

    def get_apartment_cache_key(self, apartment_id: int) -> str:
        """
        Генерация ключа кеша для детальной информации о квартире.

        Args:
            apartment_id: ID квартиры

        Returns:
            str: Ключ кеша
        """
        return get_apartment_detail_cache_key(apartment_id)

    def get_apartment_photos_cache_key(self, apartment_id: int) -> str:
        """
        Генерация ключа кеша для фотографий квартиры.

        Args:
            apartment_id: ID квартиры

        Returns:
            str: Ключ кеша
        """
        return get_apartment_photos_cache_key(apartment_id)

    def invalidate_apartments_cache(self) -> None:
        """
        Инвалидация кеша списка квартир.
        """
        self.clear_pattern("apartments:list:*")

    def invalidate_apartment_cache(self, apartment_id: int) -> None:
        """
        Инвалидация кеша квартиры.

        Args:
            apartment_id: ID квартиры
        """
        self.delete(self.get_apartment_cache_key(apartment_id))
        self.delete(self.get_apartment_photos_cache_key(apartment_id))