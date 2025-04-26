"""
Настройки для Redis и кеширования
"""
from src.config.settings import settings

# Настройки для Redis
REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

# Настройки для кеширования
CACHE_EXPIRATION = {
    "apartments_list": 300,  # 5 минут для списка квартир
    "apartment_detail": 300,  # 5 минут для детальной информации о квартире
    "apartment_photos": 600,  # 10 минут для фотографий
}

# Префиксы для ключей кеша
CACHE_KEYS = {
    "apartments_list": "apartments:list:{page}:{page_size}:{sort}:{order}",
    "apartment_detail": "apartments:detail:{id}",
    "apartment_photos": "apartments:photos:{id}",
}


# Функции для генерации ключей кеша
def get_apartments_list_cache_key(page: int, page_size: int, sort: str, order: str) -> str:
    """
    Генерирует ключ кеша для списка квартир.
    """
    return CACHE_KEYS["apartments_list"].format(
        page=page,
        page_size=page_size,
        sort=sort,
        order=order
    )


def get_apartment_detail_cache_key(apartment_id: int) -> str:
    """
    Генерирует ключ кеша для детальной информации о квартире.
    """
    return CACHE_KEYS["apartment_detail"].format(id=apartment_id)


def get_apartment_photos_cache_key(apartment_id: int) -> str:
    """
    Генерирует ключ кеша для фотографий квартиры.
    """
    return CACHE_KEYS["apartment_photos"].format(id=apartment_id)
