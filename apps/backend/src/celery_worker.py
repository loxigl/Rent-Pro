import logging
from kombu import Queue
import os
from celery import Celery
from io import BytesIO
from typing import Dict, List, Optional, Tuple
from celery.signals import task_failure

from src.services.minio_service import MinioService
from src.services.image_service import ImageService
from src.config.settings import settings

# Настройка логгера
logger = logging.getLogger(__name__)

ALL_QUEUES: dict[str, Queue] = {
    # тяжёлые CPU-bound задачи обработки картинок
    "images":  Queue("images",  routing_key="images"),
    # отправка email / push-ов
    "notifications": Queue("notifications", routing_key="notifications"),
    # генерация отчётов, экспортов, cron-подобные задачи
    "reports": Queue("reports", routing_key="reports"),
}

celery_app.conf.update(
    task_default_queue="default",                # пусть «обычные» таски идут в default
    task_queues=tuple(ALL_QUEUES.values()),
)
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

# Увеличиваем таймауты для обработки больших изображений
celery_app.conf.task_time_limit = 60 * 60  # 60 минут максимальное время выполнения
celery_app.conf.task_soft_time_limit = 30 * 60  # 30 минут мягкое ограничение

# Настройка повторных попыток при ошибках
celery_app.conf.task_acks_late = True  # Подтверждать задачи только после успешного выполнения
celery_app.conf.task_reject_on_worker_lost = True  # Возвращать задачи в очередь при потере воркера
celery_app.conf.broker_connection_retry = True  # Повторять подключение к брокеру
celery_app.conf.broker_connection_max_retries = 10  # Максимальное число попыток

# Настройка пула воркеров
celery_app.conf.worker_concurrency = 2  # Уменьшаем число параллельных обработчиков для избежания перегрузки
celery_app.conf.worker_prefetch_multiplier = 1  # Предзагрузка только 1 задачи за раз
celery_app.conf.worker_max_tasks_per_child = 100  # Перезапуск воркера после 100 задач


# Обработчик ошибок в задачах
@task_failure.connect
def handle_task_failure(task_id, exception, args, kwargs, traceback, einfo, **kw):
    logger.error(f"Task {task_id} failed: {exception}\nArgs: {args}\nKwargs: {kwargs}\n{traceback}")


@celery_app.task(name="process_image",
                 bind=True,
                 max_retries=3,
                 default_retry_delay=60,  # 1 минута между повторными попытками
                 retry_backoff=True,  # Экспоненциальная задержка между попытками
                 soft_time_limit=600,  # 10 минут soft timeout
                 time_limit=1200)  # 20 минут hard timeout
def process_image(self, file_content_bytes, apartment_id):
    """
    Задача Celery для обработки и загрузки изображения.

    Args:
        file_content_bytes: Бинарное содержимое файла
        apartment_id: ID квартиры

    Returns:
        Dict[str, str]: Словарь с URLs изображений разных размеров
    """
    try:
        logger.info(f"Processing image for apartment_id={apartment_id}, task_id={self.request.id}")

        # Проверка размера файла
        file_size_mb = len(file_content_bytes) / (1024 * 1024)
        logger.info(f"Image size: {file_size_mb:.2f} MB")

        if file_size_mb > settings.MAX_IMAGE_SIZE_MB:
            raise ValueError(f"Image too large: {file_size_mb:.2f} MB, max allowed: {settings.MAX_IMAGE_SIZE_MB} MB")

        # Создаем экземпляр сервиса MinIO
        minio_service = MinioService()

        # Загружаем изображение и получаем URLs разных размеров
        result_urls = minio_service.upload_image(file_content_bytes, apartment_id)

        # Возвращаем URL для размера small_webp для отображения в качестве обложки
        cover_url = (
                result_urls.get("small_webp") or
                result_urls.get("small_jpeg") or
                next(iter(result_urls.values()))
        )

        logger.info(f"Image processing completed successfully: {cover_url}")
        return cover_url

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        # Повторная попытка при ошибках, но не при ошибках валидации
        if not isinstance(e, ValueError):
            self.retry(exc=e)
        raise


@celery_app.task(name="reprocess_image",
                 bind=True,
                 max_retries=3,
                 default_retry_delay=60,
                 retry_backoff=True,
                 soft_time_limit=600,
                 time_limit=1200)
def reprocess_image(self, file_content_bytes, apartment_id, image_id):
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
        logger.info(f"Reprocessing image {image_id} for apartment_id={apartment_id}, task_id={self.request.id}")

        # Проверка размера файла
        file_size_mb = len(file_content_bytes) / (1024 * 1024)
        logger.info(f"Image size: {file_size_mb:.2f} MB")

        if file_size_mb > settings.MAX_IMAGE_SIZE_MB:
            raise ValueError(f"Image too large: {file_size_mb:.2f} MB, max allowed: {settings.MAX_IMAGE_SIZE_MB} MB")

        # Создаем экземпляр сервиса MinIO
        minio_service = MinioService()

        # Удаляем существующие варианты изображения с обработкой ошибок
        try:
            minio_service.delete_image(apartment_id, image_id)
        except Exception as delete_error:
            logger.warning(f"Error deleting existing image variants: {delete_error}, continuing with new upload")

        # Загружаем заново обработанное изображение
        result_urls = minio_service.upload_image(file_content_bytes, apartment_id)

        logger.info(f"Image reprocessing completed successfully")
        return result_urls

    except Exception as e:
        logger.error(f"Error reprocessing image: {e}")
        # Повторная попытка при ошибках, но не при ошибках валидации
        if not isinstance(e, ValueError):
            self.retry(exc=e)
        raise


@celery_app.task(name="bulk_reprocess_images",
                 bind=True,
                 soft_time_limit=3600,  # 1 час soft timeout
                 time_limit=7200)  # 2 часа hard timeout
def bulk_reprocess_images(self, apartment_id, max_images=None):
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
        logger.info(f"Bulk reprocessing images for apartment_id={apartment_id}, task_id={self.request.id}")

        # Создаем экземпляр сервиса MinIO
        minio_service = MinioService()

        # Для HTTP запросов
        import httpx

        # Получаем все изображения квартиры
        images = minio_service.get_apartment_images(apartment_id)

        # Ограничиваем количество изображений при необходимости
        if max_images is not None:
            images = dict(list(images.items())[:max_images])

        # Результаты обработки
        results = []

        # Для каждого изображения запускаем отдельную задачу reprocess_image
        for image_id, variants in images.items():
            # Получаем URL наиболее качественного изображения
            original_url = variants.get("original_jpeg")
            if not original_url:
                # Если нет оригинала, ищем другие варианты от лучшего к худшему
                for variant_key in ["large_jpeg", "medium_jpeg", "large_webp", "medium_webp", "small_jpeg",
                                    "small_webp"]:
                    if variant_key in variants:
                        original_url = variants[variant_key]
                        logger.info(f"Using {variant_key} as source for image_id={image_id}")
                        break

            if original_url:
                try:
                    # Загружаем файл по URL
                    logger.info(f"Downloading image from {original_url}")

                    # Используем httpx для асинхронного скачивания с таймаутом
                    # и автоматической поддержкой перенаправлений
                    timeout_settings = httpx.Timeout(30.0, connect=10.0)

                    with httpx.Client(timeout=timeout_settings, follow_redirects=True) as client:
                        response = client.get(original_url)
                        response.raise_for_status()  # Проверяем статус

                        # Получаем содержимое файла
                        file_content = response.content

                        # Проверяем размер файла
                        file_size_mb = len(file_content) / (1024 * 1024)
                        logger.info(f"Downloaded image size: {file_size_mb:.2f} MB")

                        if file_size_mb > settings.MAX_IMAGE_SIZE_MB:
                            logger.warning(
                                f"Image too large: {file_size_mb:.2f} MB, max allowed: {settings.MAX_IMAGE_SIZE_MB} MB")
                            results.append({
                                "image_id": image_id,
                                "status": "error",
                                "message": f"Image too large: {file_size_mb:.2f} MB"
                            })
                            continue

                        # Запускаем задачу reprocess_image для обработки изображения
                        logger.info(f"Starting reprocess_image task for image_id={image_id}")
                        task_result = reprocess_image.delay(file_content, apartment_id, image_id)

                        # Ждем результат с таймаутом
                        result_urls = task_result.get(timeout=600)  # 10 минут таймаут

                        results.append({
                            "image_id": image_id,
                            "status": "success",
                            "variants": list(result_urls.keys())
                        })

                except httpx.HTTPError as err:
                    logger.error(f"HTTP error downloading image {image_id}: {err}")
                    results.append({
                        "image_id": image_id,
                        "status": "error",
                        "message": f"HTTP error: {str(err)}"
                    })
                except Exception as err:
                    logger.error(f"Error processing image {image_id}: {err}")
                    results.append({
                        "image_id": image_id,
                        "status": "error",
                        "message": str(err)
                    })
            else:
                # Если нет URL оригинала, логируем ошибку
                logger.warning(f"No original image URL found for image_id={image_id}, skipping")
                results.append({
                    "image_id": image_id,
                    "status": "error",
                    "message": "No original image URL found"
                })

        logger.info(f"Bulk reprocessing completed for {len(results)} images")
        return results

    except Exception as e:
        logger.error(f"Error bulk reprocessing images: {e}")
        raise
