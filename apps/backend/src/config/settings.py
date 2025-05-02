import os
from typing import List, Tuple
from pydantic_settings import BaseSettings
from pydantic import Field


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
    DEBUG: bool = Field(False, env="DEBUG")
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

    # Параметры для кэширования
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    # Настройки JWT
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Настройки загрузки файлов
    STATIC_DIR: str = "static"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/webp"]

    # Настройки отправки email
    SMTP_ENABLED: bool = Field(False, env="SMTP_ENABLED")
    SMTP_SERVER: str = Field("smtp.gmail.com", env="SMTP_SERVER")
    SMTP_PORT: int = Field(587, env="SMTP_PORT")
    SMTP_USE_TLS: bool = Field(True, env="SMTP_USE_TLS")
    SMTP_USERNAME: str = Field("", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field("", env="SMTP_PASSWORD")
    SMTP_FROM_EMAIL: str = Field("noreply@avitorentpro.ru", env="SMTP_FROM_EMAIL")

    # Контактная информация
    SUPPORT_PHONE: str = Field("+7 (928) 123-45-67", env="SUPPORT_PHONE")
    SUPPORT_EMAIL: str = Field("support@avitorentpro.ru", env="SUPPORT_EMAIL")
    ADMIN_EMAIL: str = Field("admin@avitorentpro.ru", env="ADMIN_EMAIL")

    # URL сайта и админ-панели
    SITE_URL: str = Field("https://kvartiry26.ru", env="SITE_URL")
    ADMIN_URL: str = Field("https://admin.kvartiry26.ru", env="ADMIN_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Создаем экземпляр настроек
settings = Settings()
