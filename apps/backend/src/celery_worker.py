import logging
import os
from celery import Celery
from io import BytesIO
from typing import Dict, List, Optional

from src.services.minio_service import MinioService
from src.services.image_service import ImageService
from src.config.settings import settings

# Настройка логгера
logger = logging.getLogger(__name__)

# Настройка Celery
celery_app = Celery(
    'avitorentpro',
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0',
    backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0',
)

# Настройка задач
celery_app.conf.task_routes = {
    'process_image': {'queue': 'images'},
    'reprocess_image': {'queue': 'images'},
    'bulk_reprocess_images': {'queue': 'images'},
}

# Настройка тайм-аутов
celery_app.conf.task_time_limit = 30 * 60  # 30 минут
celery_app.conf.task_soft_time_limit = 15 * 60  # 15 минут


@celery_app.task(name="process_image")
def process_image(file_content_bytes, apartment_id):
    """
    Задача Celery для обработки и загрузки изображения.

    Args:
        file_content_bytes: Бинарное содержимое файла
        apartment_id: ID квартиры

    Returns:
        Dict[str, str]: Словарь с URLs изображений разных размеров
    """
    try:
        logger.info(f"Processing image for apartment_id={apartment_id}")

        # Создаем экземпляр сервиса MinIO
        minio_service = MinioService()

        # Загружаем изображение и получаем URLs разных размеров
        result_urls = minio_service.upload_image(file_content_bytes, apartment_id)

        # Возвращаем URL для размера small_webp для отображения в качестве обложки
        cover_url = result_urls.get("small_webp") or result_urls.get("small_jpeg") or next(iter(result_urls.values()))

        logger.info(f"Image processing completed successfully: {cover_url}")
        return cover_url

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise


@celery_app.task(name="reprocess_image")
def reprocess_image(file_content_bytes, apartment_id, image_id):
    """
    Задача Celery для повторной обработки существующего изображения.

    Args:
        file_content_bytes: Бинарное содержимое файла
        apartment_id: ID квартиры
        image_id: ID изображения

    Returns:
        Dict[str, str]: Словарь с URLs изображений разных размеров
    """
    try:
        logger.info(f"Reprocessing image {image_id} for apartment_id={apartment_id}")

        # Создаем экземпляр сервиса MinIO
        minio_service = MinioService()

        # Удаляем существующие варианты изображения
        minio_service.delete_image(apartment_id, image_id)

        # Загружаем заново обработанное изображение
        result_urls = minio_service.upload_image(file_content_bytes, apartment_id)

        logger.info(f"Image reprocessing completed successfully")
        return result_urls

    except Exception as e:
        logger.error(f"Error reprocessing image: {e}")
        raise


@celery_app.task(name="bulk_reprocess_images")
def bulk_reprocess_images(apartment_id, max_images=None):
    """
    Задача Celery для повторной обработки всех изображений квартиры.
    Используется при изменении алгоритма обработки или требований к изображениям.

    Args:
        apartment_id: ID квартиры
        max_images: Максимальное количество изображений для обработки (None - все)

    Returns:
        List[Dict[str, str]]: Список словарей с URLs изображений разных размеров
    """
    try:
        logger.info(f"Bulk reprocessing images for apartment_id={apartment_id}")

        # Создаем экземпляр сервиса MinIO
        minio_service = MinioService()

        # Получаем все изображения квартиры
        images = minio_service.get_apartment_images(apartment_id)

        # Ограничиваем количество изображений при необходимости
        if max_images is not None:
            images = dict(list(images.items())[:max_images])

        # Результаты обработки
        results = []

        # Для каждого изображения запускаем отдельную задачу reprocess_image
        for image_id, variants in images.items():
            # Получаем оригинальное изображение
            original_url = variants.get("original_jpeg")
            if original_url:
                # Загружаем файл
                # Здесь предполагается, что original_url доступен напрямую
                # В реальном сценарии, возможно, потребуется использовать presigned URL
                # или получить файл из MinIO напрямую
                # Этот код упрощен для примера
                # TODO: Реализовать правильную загрузку файла

                # Запускаем задачу reprocess_image
                task = reprocess_image.delay(b"file_content", apartment_id, image_id)
                result = task.get()
                results.append(result)

        logger.info(f"Bulk reprocessing completed for {len(results)} images")
        return results

    except Exception as e:
        logger.error(f"Error bulk reprocessing images: {e}")
        raise
