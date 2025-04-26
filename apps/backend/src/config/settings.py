import os
from typing import List, Tuple

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # База данных
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "avitorentpro"

    @property
    def DATABASE_URL(self) -> str:
        """Получить строку подключения к базе данных."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # MinIO / S3
    MINIO_ROOT_USER: str = "minio"
    MINIO_ROOT_PASSWORD: str = "minio123"
    MINIO_HOST: str = "minio"
    MINIO_PORT: int = 9000
    MINIO_BUCKET: str = "apartments"
    MINIO_USE_SSL: bool = False

    # URL для публичного доступа к фотографиям
    PHOTOS_BASE_URL: str = "http://localhost:9000/apartments"

    # Параметры приложения
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    PROJECT_NAME: str = "AvitoRentPro"

    # Параметры для обработки изображений
    MAX_IMAGE_SIZE_MB: int = 10
    MAX_IMAGE_DIMENSION: int = 1920

    # Параметры для вариантов изображений
    IMAGE_FORMATS: List[str] = ["jpeg", "webp"]
    THUMBNAIL_SIZE: Tuple[int, int] = (150, 150)
    SMALL_WIDTH: int = 400
    MEDIUM_WIDTH: int = 800
    LARGE_WIDTH: int = 1200

    # Параметры качества изображений
    JPEG_QUALITY: int = 85  # 0-100
    WEBP_QUALITY: int = 80  # 0-100

    class Config:
        env_file = ".env"


# Создаем экземпляр настроек
settings = Settings()