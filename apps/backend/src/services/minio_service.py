import uuid
from io import BytesIO
import logging
from typing import Dict, List, Optional
from minio import Minio
from minio.error import S3Error

from src.config.settings import settings
from src.services.image_service import ImageService, ImageSize, ImageFormat

logger = logging.getLogger(__name__)


class MinioService:
    """Сервис для работы с MinIO/S3 хранилищем."""

    def __init__(self):
        self.client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_USE_SSL
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Проверяет, существует ли бакет, и создает его при необходимости."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Bucket '{self.bucket_name}' created successfully")

                # Устанавливаем политику доступа только для чтения
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                        }
                    ]
                }
                self.client.set_bucket_policy(self.bucket_name, policy)
            else:
                logger.info(f"Bucket '{self.bucket_name}' already exists")
        except S3Error as err:
            logger.error(f"Error checking/creating bucket: {err}")
            raise

    def upload_image(self, file_content: bytes, apartment_id: int) -> Dict[str, str]:
        """
        Загружает изображение и его варианты в хранилище.

        Args:
            file_content: Бинарное содержимое файла
            apartment_id: ID квартиры

        Returns:
            Dict[str, str]: Словарь с URLs вариантов изображения {size_format: url}
        """
        try:
            # Получаем информацию об изображении
            image_info = ImageService.get_image_info(file_content)

            # Обрабатываем изображение, получаем различные варианты
            processed_images = ImageService.process_image(file_content)

            # Загружаем все варианты в MinIO
            result_urls = {}

            for variant, variant_content in processed_images.items():
                # Генерируем имя файла
                file_path = ImageService.generate_image_filename(apartment_id, variant)

                # Определяем MIME тип
                content_type = "image/webp" if "webp" in variant else "image/jpeg"

                # Готовим метаданные
                metadata = {
                    "original-width": str(image_info.get("width", 0)),
                    "original-height": str(image_info.get("height", 0)),
                    "apartment-id": str(apartment_id),
                    "variant": variant
                }

                # Загружаем файл в MinIO
                self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=file_path,
                    data=BytesIO(variant_content),
                    length=len(variant_content),
                    content_type=content_type,
                    metadata=metadata
                )

                # Формируем URL для доступа к изображению
                file_url = f"{settings.PHOTOS_BASE_URL}/{file_path}"
                result_urls[variant] = file_url

            logger.info(f"Uploaded {len(result_urls)} image variants for apartment_id={apartment_id}")
            return result_urls

        except S3Error as err:
            logger.error(f"Error uploading image to MinIO: {err}")
            raise
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise

    def get_apartment_images(self, apartment_id: int) -> Dict[str, Dict[str, str]]:
        """
        Получает все изображения квартиры.

        Args:
            apartment_id: ID квартиры

        Returns:
            Dict[str, Dict[str, str]]: Словарь {image_id: {variant: url}}
        """
        try:
            prefix = f"apartments/{apartment_id}/"
            objects = self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True)

            # Группируем по image_id (uuid части имени файла)
            images = {}

            for obj in objects:
                object_name = obj.object_name

                # Извлекаем UUID из имени файла
                parts = object_name.split('/')
                if len(parts) >= 3:
                    filename = parts[-1]
                    # Получаем UUID и вариант из имени файла
                    file_parts = filename.split('_', 1)
                    image_id = file_parts[0]

                    # Если есть вариант, извлекаем его
                    variant = None
                    if len(file_parts) > 1:
                        variant = file_parts[1].rsplit('.', 1)[0]
                    else:
                        variant = "original_jpeg"

                    # Добавляем в словарь
                    if image_id not in images:
                        images[image_id] = {}

                    # Формируем URL для доступа к изображению
                    file_url = f"{settings.PHOTOS_BASE_URL}/{object_name}"
                    images[image_id][variant] = file_url

            return images

        except S3Error as err:
            logger.error(f"Error getting apartment images: {err}")
            raise

    def get_image_variants(self, apartment_id: int, image_id: str) -> Dict[str, str]:
        """
        Получает все варианты одного изображения.

        Args:
            apartment_id: ID квартиры
            image_id: ID изображения (UUID часть имени файла)

        Returns:
            Dict[str, str]: Словарь {variant: url}
        """
        try:
            prefix = f"apartments/{apartment_id}/{image_id}"
            objects = self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True)

            variants = {}

            for obj in objects:
                object_name = obj.object_name

                # Извлекаем вариант из имени файла
                parts = object_name.split('_', 1)
                variant = None
                if len(parts) > 1:
                    variant = parts[1].rsplit('.', 1)[0]
                else:
                    variant = "original_jpeg"

                # Формируем URL для доступа к изображению
                file_url = f"{settings.PHOTOS_BASE_URL}/{object_name}"
                variants[variant] = file_url

            return variants

        except S3Error as err:
            logger.error(f"Error getting image variants: {err}")
            raise

    def generate_presigned_url(self, object_name: str, expires: int = 86400) -> str:
        """
        Генерирует подписанный URL для доступа к объекту.

        Args:
            object_name: Имя объекта в хранилище
            expires: Время действия URL в секундах (по умолчанию 24 часа)

        Returns:
            str: Подписанный URL
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as err:
            logger.error(f"Error generating presigned URL: {err}")
            raise

    def delete_image(self, apartment_id: int, image_id: str) -> bool:
        """
        Удаляет все варианты изображения из хранилища.

        Args:
            apartment_id: ID квартиры
            image_id: ID изображения (UUID часть имени файла)

        Returns:
            bool: Успешно или нет
        """
        try:
            # Получаем список всех вариантов изображения
            prefix = f"apartments/{apartment_id}/{image_id}"
            objects = self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True)

            # Удаляем все объекты
            for obj in objects:
                self.client.remove_object(
                    bucket_name=self.bucket_name,
                    object_name=obj.object_name
                )

            logger.info(f"Image {image_id} for apartment {apartment_id} deleted successfully")
            return True

        except S3Error as err:
            logger.error(f"Error deleting image: {err}")
            return False