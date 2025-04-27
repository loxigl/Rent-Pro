"""
Оптимизированная версия ImageService для эффективной обработки изображений
"""

import io
import uuid
import logging
from typing import Dict, List, Tuple, Optional
from enum import Enum
from PIL import Image, ImageOps, ExifTags, ImageFile
import piexif
import time

from src.config.settings import settings

# Разрешить обработку изображений с неполной информацией
ImageFile.LOAD_TRUNCATED_IMAGES = True

logger = logging.getLogger(__name__)


class ImageSize(str, Enum):
    """Перечисление размеров изображений."""
    THUMBNAIL = "thumbnail"  # 150x150, для превью в сетке
    SMALL = "small"  # 400px по ширине, для карточек
    MEDIUM = "medium"  # 800px по ширине, для деталей
    LARGE = "large"  # 1200px по ширине, для просмотра
    ORIGINAL = "original"  # Оригинальный размер, но не более MAX_IMAGE_DIMENSION


class ImageFormat(str, Enum):
    """Перечисление форматов изображений."""
    JPEG = "jpeg"
    WEBP = "webp"
    PNG = "png"


class ImageService:
    """Сервис для обработки изображений."""

    @staticmethod
    def process_image(file_content: bytes) -> Dict[str, bytes]:
        """
        Обрабатывает изображение, создает различные размеры и форматы.

        Args:
            file_content: Бинарное содержимое файла

        Returns:
            Dict[str, bytes]: Словарь с вариантами изображения {size_format: content}
        """
        start_time = time.time()
        try:
            # Открываем изображение
            img = Image.open(io.BytesIO(file_content))

            # Проверяем размер изображения
            width, height = img.size
            if width > settings.MAX_IMAGE_DIMENSION or height > settings.MAX_IMAGE_DIMENSION:
                logger.info(f"Image size {width}x{height} exceeds maximum dimension, resizing")
                img = ImageService._resize_to_max_dimension(img, settings.MAX_IMAGE_DIMENSION)
                width, height = img.size
                logger.info(f"Resized to {width}x{height}")

            # Сохраняем EXIF данные
            exif_data = None
            if "exif" in img.info:
                exif_data = img.info["exif"]

            # Автоматически поворачиваем изображение по EXIF
            img = ImageOps.exif_transpose(img)

            # Словарь для хранения результатов
            result = {}

            # Приоритетные варианты (нужны всегда)
            priority_variants = [
                (ImageSize.THUMBNAIL, ImageFormat.WEBP),
                (ImageSize.SMALL, ImageFormat.WEBP),
                (ImageSize.ORIGINAL, ImageFormat.JPEG)
            ]

            # Обрабатываем приоритетные варианты
            for size, fmt in priority_variants:
                variant_key = f"{size.value}_{fmt.value}"
                result[variant_key] = ImageService._create_variant(img, size, fmt, exif_data)

            # Дополнительные варианты (для производительности создаем только если нужно)
            optional_variants = [
                (ImageSize.MEDIUM, ImageFormat.WEBP),
                (ImageSize.LARGE, ImageFormat.WEBP),
                (ImageSize.SMALL, ImageFormat.JPEG),
                (ImageSize.MEDIUM, ImageFormat.JPEG)
            ]

            # Создаем дополнительные варианты с контролем времени
            for size, fmt in optional_variants:
                # Если времени прошло больше 30 секунд, прекращаем создание доп. вариантов
                if time.time() - start_time > 30:
                    logger.warning("Image processing time exceeded 30s limit, skipping remaining variants")
                    break

                variant_key = f"{size.value}_{fmt.value}"
                result[variant_key] = ImageService._create_variant(img, size, fmt, exif_data)

            logger.info(f"Created {len(result)} image variants in {time.time() - start_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise

    @staticmethod
    def _create_variant(img: Image.Image, size: ImageSize, fmt: ImageFormat, exif_data: Optional[bytes]) -> bytes:
        """
        Создает один вариант изображения определенного размера и формата.

        Args:
            img: Исходное изображение
            size: Размер варианта
            fmt: Формат варианта
            exif_data: EXIF данные (только для JPEG)

        Returns:
            bytes: Бинарные данные обработанного изображения
        """
        start_time = time.time()

        try:
            # Изменяем размер изображения
            resized_img = ImageService._resize_image(img, size)

            # Сохраняем в нужном формате
            output = io.BytesIO()

            if fmt == ImageFormat.WEBP:
                # Параметры для WebP
                save_params = {
                    "quality": settings.WEBP_QUALITY,
                    "method": 4,  # Баланс между скоростью и качеством (0-6)
                    "lossless": False
                }
                resized_img.save(output, format="WEBP", **save_params)

            elif fmt == ImageFormat.JPEG:
                # Параметры для JPEG
                save_params = {
                    "quality": settings.JPEG_QUALITY,
                    "optimize": True,
                    "progressive": True
                }

                # Добавляем EXIF для оригинального размера, если они есть
                if size == ImageSize.ORIGINAL and exif_data:
                    save_params["exif"] = exif_data

                resized_img.save(output, format="JPEG", **save_params)

            else:
                # По умолчанию сохраняем как JPEG
                resized_img.save(output, format="JPEG", quality=settings.JPEG_QUALITY, optimize=True)

            output.seek(0)
            result = output.getvalue()

            # Логируем размер и время
            size_kb = len(result) / 1024
            logger.debug(f"Created {size.value}_{fmt.value} variant ({size_kb:.1f}KB) in {time.time() - start_time:.2f}s")

            return result

        except Exception as e:
            logger.error(f"Error creating {size.value}_{fmt.value} variant: {e}")
            # В случае ошибки возвращаем пустой результат
            raise

    @staticmethod
    def _resize_image(img: Image.Image, size: ImageSize) -> Image.Image:
        """
        Изменяет размер изображения в соответствии с указанным типом размера.

        Args:
            img: Исходное изображение
            size: Тип размера

        Returns:
            Image.Image: Изображение с измененным размером
        """
        # Получаем оригинальные размеры
        width, height = img.size

        # Определяем новые размеры в зависимости от типа
        if size == ImageSize.THUMBNAIL:
            # Для thumbnail создаем квадратное изображение 150x150
            return ImageService._create_thumbnail(img, (settings.THUMBNAIL_SIZE[0], settings.THUMBNAIL_SIZE[1]))

        elif size == ImageSize.SMALL:
            # Стандартно 400px по ширине
            return ImageService._resize_proportionally(img, settings.SMALL_WIDTH)

        elif size == ImageSize.MEDIUM:
            # Стандартно 800px по ширине
            return ImageService._resize_proportionally(img, settings.MEDIUM_WIDTH)

        elif size == ImageSize.LARGE:
            # Стандартно 1200px по ширине
            return ImageService._resize_proportionally(img, settings.LARGE_WIDTH)

        elif size == ImageSize.ORIGINAL:
            # Оригинальный размер, но не более MAX_IMAGE_DIMENSION
            return ImageService._resize_to_max_dimension(img, settings.MAX_IMAGE_DIMENSION)

        # По умолчанию возвращаем оригинал
        return img

    @staticmethod
    def _resize_to_max_dimension(img: Image.Image, max_dimension: int) -> Image.Image:
        """
        Изменяет размер изображения так, чтобы наибольшая сторона не превышала max_dimension
        с сохранением пропорций.

        Args:
            img: Исходное изображение
            max_dimension: Максимальный размер стороны

        Returns:
            Image.Image: Изображение с измененным размером
        """
        width, height = img.size

        # Если изображение уже достаточно маленькое, ничего не делаем
        if width <= max_dimension and height <= max_dimension:
            return img

        # Определяем, какая сторона больше
        if width > height:
            # Ширина больше, вычисляем новую высоту
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            # Высота больше, вычисляем новую ширину
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))

        # Изменяем размер
        return img.resize((new_width, new_height), Image.LANCZOS)

    @staticmethod
    def _resize_proportionally(img: Image.Image, target_width: int) -> Image.Image:
        """
        Пропорционально изменяет размер изображения до указанной ширины.

        Args:
            img: Исходное изображение
            target_width: Целевая ширина

        Returns:
            Image.Image: Изображение с измененным размером
        """
        width, height = img.size

        # Если изображение уже меньше целевой ширины, оставляем как есть
        if width <= target_width:
            return img

        # Вычисляем новую высоту с сохранением пропорций
        new_height = int(height * (target_width / width))

        # Изменяем размер
        return img.resize((target_width, new_height), Image.LANCZOS)

    @staticmethod
    def _create_thumbnail(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """
        Создает миниатюру с кропом по центру.

        Args:
            img: Исходное изображение
            size: Размер миниатюры (ширина, высота)

        Returns:
            Image.Image: Миниатюра
        """
        # Создаем копию изображения для безопасности
        img_copy = img.copy()

        # Конвертируем в RGB, если это RGBA
        if img_copy.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img_copy.size, (255, 255, 255))
            background.paste(img_copy, mask=img_copy.split()[3])
            img_copy = background

        # Определяем, по какой стороне масштабировать для сохранения пропорций
        width, height = img_copy.size
        target_width, target_height = size
        ratio = max(target_width / width, target_height / height)

        # Масштабируем изображение так, чтобы оно содержало весь целевой размер
        new_size = (int(width * ratio), int(height * ratio))

        # Изменяем размер изображения
        img_copy = img_copy.resize(new_size, Image.LANCZOS)

        # Делаем кроп по центру
        width, height = img_copy.size
        left = (width - target_width) // 2
        top = (height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        return img_copy.crop((left, top, right, bottom))

    @staticmethod
    def get_image_info(file_content: bytes) -> Dict:
        """
        Получает информацию об изображении.

        Args:
            file_content: Бинарное содержимое файла

        Returns:
            Dict: Информация об изображении
        """
        try:
            # Используем контекстный менеджер для автоматического закрытия ресурсов
            with Image.open(io.BytesIO(file_content)) as img:
                info = {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_kb": len(file_content) / 1024
                }

                # Добавляем EXIF данные, если они есть
                if "exif" in img.info:
                    try:
                        exif_dict = piexif.load(img.info["exif"])
                        exif_info = {}

                        # Получаем основные EXIF данные (упрощенно)
                        if "0th" in exif_dict:
                            # Добавляем только важные теги для упрощения
                            important_tags = ["Make", "Model", "Orientation", "DateTime"]
                            for tag in important_tags:
                                tag_id = next((k for k, v in ExifTags.TAGS.items() if v == tag), None)
                                if tag_id and tag_id in exif_dict["0th"]:
                                    val = exif_dict["0th"][tag_id]
                                    if isinstance(val, bytes):
                                        try:
                                            val = val.decode("utf-8", errors="replace")
                                        except:
                                            val = str(val)
                                    exif_info[tag] = val

                        info["exif"] = exif_info
                    except Exception as exif_error:
                        logger.warning(f"Error parsing EXIF data: {exif_error}")
                        info["exif"] = {"error": str(exif_error)}

                return info

        except Exception as e:
            logger.error(f"Error getting image info: {e}")
            return {"error": str(e)}

    @staticmethod
    def generate_image_filename(apartment_id: int, variant: str = None) -> str:
        """
        Генерирует имя файла для изображения.

        Args:
            apartment_id: ID квартиры
            variant: Вариант изображения (size_format)

        Returns:
            str: Имя файла
        """
        file_uuid = str(uuid.uuid4())
        if variant:
            extension = "webp" if "webp" in variant else "jpg"
            return f"apartments/{apartment_id}/{file_uuid}_{variant}.{extension}"
        return f"apartments/{apartment_id}/{file_uuid}.jpg"

    @staticmethod
    def optimize_original_image(file_content: bytes) -> Image.Image:
        """
        Оптимизирует оригинальное изображение, сохраняя EXIF и уменьшая размер при необходимости.

        Args:
            file_content: Бинарное содержимое файла

        Returns:
            Image.Image: Оптимизированное изображение
        """
        img = Image.open(io.BytesIO(file_content))

        # Автоповорот по EXIF
        img = ImageOps.exif_transpose(img)

        # Проверяем размер и уменьшаем при необходимости
        width, height = img.size
        max_dim = settings.MAX_IMAGE_DIMENSION

        if width > max_dim or height > max_dim:
            img = ImageService._resize_to_max_dimension(img, max_dim)

        # Если изображение в RGBA, конвертируем в RGB
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
            img = background

        return img

    @staticmethod
    def create_image_variant(file_content: bytes, size: ImageSize, fmt: ImageFormat) -> bytes:
        """
        Создает конкретный вариант изображения напрямую из бинарного содержимого.

        Args:
            file_content: Бинарное содержимое файла
            size: Размер варианта
            fmt: Формат варианта

        Returns:
            bytes: Бинарные данные обработанного изображения
        """
        try:
            # Открываем изображение и автоматически поворачиваем
            img = Image.open(io.BytesIO(file_content))
            img = ImageOps.exif_transpose(img)

            # Создаем вариант
            resized_img = ImageService._resize_image(img, size)

            # Сохраняем в нужном формате
            output = io.BytesIO()

            if fmt == ImageFormat.WEBP:
                resized_img.save(
                    output,
                    format="WEBP",
                    quality=settings.WEBP_QUALITY,
                    method=4  # Баланс между скоростью и качеством
                )
            else:
                resized_img.save(
                    output,
                    format="JPEG",
                    quality=settings.JPEG_QUALITY,
                    optimize=True,
                    progressive=True
                )

            output.seek(0)
            return output.getvalue()

        except Exception as e:
            logger.error(f"Error creating image variant {size.value}_{fmt.value}: {e}")
            raise