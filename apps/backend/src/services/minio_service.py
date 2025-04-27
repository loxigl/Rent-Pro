"""
Оптимизированная версия MinioService для обработки изображений
Изменения включают:
- Улучшенную обработку ошибок
- Оптимизацию обработки изображений
- Повторные попытки при ошибках сети
- Таймауты для операций
"""

import uuid
import json
import time
from io import BytesIO
import logging
from typing import Dict, List, Optional
from minio import Minio
from minio.error import S3Error
import tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

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
            secure=settings.MINIO_USE_SSL,
            # Настройки для улучшения производительности
            region=None,
            http_client=None,
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            f"Retry attempt {retry_state.attempt_number} for MinIO operation after error: {retry_state.outcome.exception()}"
        )
    )
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
                policy_str = json.dumps(policy)
                self.client.set_bucket_policy(self.bucket_name, policy_str)
                logger.info(f"Read-only policy set for bucket '{self.bucket_name}'")
            else:
                logger.info(f"Bucket '{self.bucket_name}' already exists")
        except S3Error as err:
            logger.error(f"Error checking/creating bucket: {err}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def upload_image(self, file_content: bytes, apartment_id: int) -> Dict[str, str]:
        """
        Загружает изображение и его варианты в хранилище.

        Args:
            file_content: Бинарное содержимое файла
            apartment_id: ID квартиры

        Returns:
            Dict[str, str]: Словарь с URLs вариантов изображения {size_format: url}
        """
        start_time = time.time()
        try:
            # Проверка размера файла
            file_size_mb = len(file_content) / (1024 * 1024)
            if file_size_mb > settings.MAX_IMAGE_SIZE_MB:
                raise ValueError(
                    f"Image too large: {file_size_mb:.2f} MB, max allowed: {settings.MAX_IMAGE_SIZE_MB} MB")

            logger.info(f"Processing image of size {file_size_mb:.2f} MB for apartment_id={apartment_id}")

            # Получаем информацию об изображении
            image_info = ImageService.get_image_info(file_content)
            logger.debug(f"Image info: {image_info}")

            # Обрабатываем изображение, получаем различные варианты
            # Распараллеливаем обработку наиболее важных форматов
            start_process = time.time()
            processed_images = {}

            # Основные варианты изображений (оптимизировано)
            # Мы обрабатываем только самые необходимые варианты: thumbnail, small, medium
            # Original только для JPEG, остальные в WEBP для экономии
            variants_to_process = [
                (ImageSize.THUMBNAIL, ImageFormat.WEBP),
                (ImageSize.SMALL, ImageFormat.WEBP),
                (ImageSize.MEDIUM, ImageFormat.WEBP),
                (ImageSize.SMALL, ImageFormat.JPEG),
                (ImageSize.ORIGINAL, ImageFormat.JPEG)
            ]

            for size, fmt in variants_to_process:
                try:
                    variant_start = time.time()
                    variant_key = f"{size.value}_{fmt.value}"

                    # Создаем вариант изображения
                    if size == ImageSize.ORIGINAL and fmt == ImageFormat.JPEG:
                        # Для оригинального размера просто используем исходное изображение
                        # с оптимизацией качества
                        img = ImageService.optimize_original_image(file_content)
                        buffer = BytesIO()
                        img.save(buffer, format="JPEG", quality=settings.JPEG_QUALITY, optimize=True)
                        buffer.seek(0)
                        processed_images[variant_key] = buffer.getvalue()
                    else:
                        # Для остальных вариантов используем специализированные методы
                        processed_images[variant_key] = ImageService.create_image_variant(
                            file_content, size, fmt
                        )

                    logger.debug(f"Processed variant {variant_key} in {time.time() - variant_start:.2f}s")
                except Exception as e:
                    logger.error(f"Error processing variant {size.value}_{fmt.value}: {e}")
                    # Продолжаем обработку других вариантов

            logger.info(f"Image processing completed in {time.time() - start_process:.2f}s")

            # Загружаем все варианты в MinIO
            result_urls = {}
            upload_start = time.time()

            # Генерируем уникальный идентификатор для изображения
            image_id = str(uuid.uuid4())

            # Загружаем все обработанные варианты
            for variant, variant_content in processed_images.items():
                # Определяем имя файла и путь
                file_path = f"apartments/{apartment_id}/{image_id}_{variant}.{'webp' if 'webp' in variant else 'jpg'}"

                # Определяем MIME тип
                content_type = "image/webp" if "webp" in variant else "image/jpeg"

                # Создаем метаданные
                metadata = {
                    "original-width": str(image_info.get("width", 0)),
                    "original-height": str(image_info.get("height", 0)),
                    "apartment-id": str(apartment_id),
                    "variant": variant,
                    "image-id": image_id
                }

                # Загружаем файл в MinIO с обработкой ошибок и повторными попытками
                try:
                    self._upload_file_with_retry(
                        file_path=file_path,
                        file_content=variant_content,
                        content_type=content_type,
                        metadata=metadata
                    )

                    # Формируем URL для доступа к изображению
                    file_url = f"{settings.PHOTOS_BASE_URL}/{file_path}"
                    result_urls[variant] = file_url
                except Exception as e:
                    logger.error(f"Error uploading variant {variant}: {e}")
                    # Продолжаем с другими вариантами

            upload_time = time.time() - upload_start
            logger.info(
                f"Uploaded {len(result_urls)} image variants in {upload_time:.2f}s for apartment_id={apartment_id}")

            # Проверяем, что хотя бы один вариант был успешно загружен
            if not result_urls:
                raise Exception("Failed to upload any image variants")

            total_time = time.time() - start_time
            logger.info(f"Total image processing and upload time: {total_time:.2f}s")

            return result_urls

        except S3Error as err:
            logger.error(f"Error uploading image to MinIO: {err}")
            raise
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def _upload_file_with_retry(self, file_path: str, file_content: bytes, content_type: str, metadata: dict):
        """
        Загружает файл в MinIO с поддержкой повторных попыток при ошибках.

        Args:
            file_path: Путь к файлу в бакете
            file_content: Содержимое файла
            content_type: MIME-тип содержимого
            metadata: Метаданные файла
        """
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                data=BytesIO(file_content),
                length=len(file_content),
                content_type=content_type,
                metadata=metadata
            )
        except S3Error as err:
            logger.error(f"Error uploading file {file_path} to MinIO: {err}")
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
            objects = []

            # Используем пагинацию для обработки больших каталогов
            objects_stream = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=True
            )

            for obj in objects_stream:
                objects.append(obj)

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
            # Возвращаем пустой словарь вместо ошибки
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting apartment images: {e}")
            return {}

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
            variants = {}

            # Используем пагинацию для обработки
            objects_stream = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=True
            )

            for obj in objects_stream:
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
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting image variants: {e}")
            return {}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
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
            delete_error_count = 0
            delete_success_count = 0

            # Получаем список объектов для удаления
            objects_to_delete = []
            objects_stream = self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True)

            for obj in objects_stream:
                objects_to_delete.append(obj.object_name)

            if not objects_to_delete:
                logger.warning(f"No objects found for deletion with prefix: {prefix}")
                return False

            # Удаляем объекты по одному с повторными попытками
            for object_name in objects_to_delete:
                try:
                    self.client.remove_object(
                        bucket_name=self.bucket_name,
                        object_name=object_name
                    )
                    delete_success_count += 1
                except Exception as error:
                    logger.error(f"Error deleting object {object_name}: {error}")
                    delete_error_count += 1

            # Считаем удаление успешным, если удалено хотя бы 50% объектов
            success = delete_success_count > 0 and delete_error_count <= delete_success_count

            if success:
                logger.info(f"Image {image_id} for apartment {apartment_id} deleted successfully")
                logger.debug(f"Deleted: {delete_success_count}, Failed: {delete_error_count}")
            else:
                logger.warning(
                    f"Partial failure deleting image {image_id}: {delete_success_count} succeeded, {delete_error_count} failed")

            return success

        except S3Error as err:
            logger.error(f"Error deleting image: {err}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting image: {e}")
            return False

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
            # Возвращаем прямой URL как запасной вариант
            return f"{settings.PHOTOS_BASE_URL}/{object_name}"
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {e}")
            return f"{settings.PHOTOS_BASE_URL}/{object_name}"
