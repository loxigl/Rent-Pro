import io
import uuid
import logging
from typing import Dict, List, Tuple, Optional
from enum import Enum
from PIL import Image, ImageOps, ExifTags
import piexif

from src.config.settings import settings

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
        try:
            # Открываем изображение
            img = Image.open(io.BytesIO(file_content))

            # Сохраняем EXIF данные
            exif_data = None
            if "exif" in img.info:
                exif_data = img.info["exif"]

            # Автоматически поворачиваем изображение по EXIF
            img = ImageOps.exif_transpose(img)

            # Словарь для хранения результатов
            result = {}

            # Обрабатываем различные размеры и форматы
            for size in ImageSize:
                for fmt in [ImageFormat.JPEG, ImageFormat.WEBP]:
                    # Пропускаем некоторые комбинации для оптимизации
                    if size == ImageSize.ORIGINAL and fmt != ImageFormat.JPEG:
                        continue

                    # Создаем версию изображения нужного размера
                    resized_img = ImageService._resize_image(img, size)

                    # Сохраняем в нужном формате
                    output = io.BytesIO()
                    save_params = {"quality": 85, "optimize": True}

                    # Для JPEG сохраняем EXIF данные
                    if fmt == ImageFormat.JPEG and exif_data and size == ImageSize.ORIGINAL:
                        save_params["exif"] = exif_data

                    # Для WEBP устанавливаем оптимальные параметры
                    if fmt == ImageFormat.WEBP:
                        save_params["method"] = 6  # Более медленное, но лучшее сжатие

                    # Сохраняем изображение
                    if fmt == ImageFormat.WEBP:
                        resized_img.save(output, format="WEBP", **save_params)
                    else:
                        resized_img.save(output, format="JPEG", **save_params)

                    output.seek(0)
                    result[f"{size.value}_{fmt.value}"] = output.getvalue()

            return result

        except Exception as e:
            logger.error(f"Error processing image: {e}")
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
            return ImageService._create_thumbnail(img, (150, 150))

        elif size == ImageSize.SMALL:
            # 400px по ширине
            return ImageService._resize_proportionally(img, 400)

        elif size == ImageSize.MEDIUM:
            # 800px по ширине
            return ImageService._resize_proportionally(img, 800)

        elif size == ImageSize.LARGE:
            # 1200px по ширине
            return ImageService._resize_proportionally(img, 1200)

        elif size == ImageSize.ORIGINAL:
            # Оригинальный размер, но не более MAX_IMAGE_DIMENSION
            max_dim = settings.MAX_IMAGE_DIMENSION
            if width > max_dim or height > max_dim:
                return ImageService._resize_proportionally(img, max_dim)
            return img

        # По умолчанию возвращаем оригинал
        return img

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

        # Создаем thumbnail с сохранением пропорций
        img_copy.thumbnail((max(size), max(size)), Image.LANCZOS)

        # Если размеры не соответствуют целевым, делаем кроп по центру
        width, height = img_copy.size
        target_width, target_height = size

        if width != target_width or height != target_height:
            left = (width - target_width) // 2
            top = (height - target_height) // 2
            right = (width + target_width) // 2
            bottom = (height + target_height) // 2

            # Убеждаемся, что координаты в пределах изображения
            left = max(0, left)
            top = max(0, top)
            right = min(width, right)
            bottom = min(height, bottom)

            # Делаем кроп
            img_copy = img_copy.crop((left, top, right, bottom))

            # Если после кропа размеры всё еще не соответствуют, делаем resize
            if img_copy.size != size:
                img_copy = img_copy.resize(size, Image.LANCZOS)

        return img_copy

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
            with Image.open(io.BytesIO(file_content)) as img:
                info = {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                }

                # Добавляем EXIF данные, если они есть
                if "exif" in img.info:
                    exif_dict = piexif.load(img.info["exif"])
                    exif_info = {}

                    # Получаем основные EXIF данные
                    if "0th" in exif_dict:
                        for tag, val in exif_dict["0th"].items():
                            tag_name = ExifTags.TAGS.get(tag, str(tag))
                            if isinstance(val, bytes):
                                try:
                                    val = val.decode("utf-8", errors="replace")
                                except:
                                    val = str(val)
                            exif_info[tag_name] = val

                    info["exif"] = exif_info

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