"""
Сервис для обработки различных форматов изображений
Поддерживает конвертацию HEIC, AVIF, TIFF, BMP и других форматов в JPEG/WebP
"""

import io
import logging
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageOps
import pillow_heif
from enum import Enum

logger = logging.getLogger(__name__)

# Регистрируем плагин для поддержки HEIC/HEIF
pillow_heif.register_heif_opener()


class SupportedInputFormat(str, Enum):
    """Поддерживаемые входные форматы"""
    JPEG = "image/jpeg"
    JPG = "image/jpg"
    PNG = "image/png"
    WEBP = "image/webp"
    HEIC = "image/heic"
    HEIF = "image/heif"
    AVIF = "image/avif"
    TIFF = "image/tiff"
    TIF = "image/tif"
    BMP = "image/bmp"
    GIF = "image/gif"
    ICO = "image/x-icon"
    # Добавляем дополнительные форматы
    JPEG2000 = "image/jp2"
    PSD = "image/vnd.adobe.photoshop"
    SVG = "image/svg+xml"


class ImageFormatService:
    """Сервис для обработки различных форматов изображений"""
    
    # Мапинг MIME типов к расширениям
    MIME_TO_EXTENSION = {
        "image/jpeg": "jpg",
        "image/jpg": "jpg", 
        "image/png": "png",
        "image/webp": "webp",
        "image/heic": "heic",
        "image/heif": "heif",
        "image/avif": "avif",
        "image/tiff": "tiff",
        "image/tif": "tiff",
        "image/bmp": "bmp",
        "image/gif": "gif",
        "image/x-icon": "ico",
        "image/jp2": "jp2",
        "image/vnd.adobe.photoshop": "psd",
        "image/svg+xml": "svg"
    }
    
    # Форматы, которые не поддерживаются для конвертации
    UNSUPPORTED_FORMATS = {
        "image/svg+xml",  # SVG - векторный формат
        "image/vnd.adobe.photoshop"  # PSD - многослойный формат
    }
    
    @staticmethod
    def is_supported_format(content_type: str) -> bool:
        """
        Проверяет, поддерживается ли формат изображения
        
        Args:
            content_type: MIME тип файла
            
        Returns:
            bool: True если формат поддерживается
        """
        return content_type.lower() in [fmt.value for fmt in SupportedInputFormat]
    
    @staticmethod
    def get_supported_formats() -> list[str]:
        """
        Возвращает список всех поддерживаемых MIME типов
        
        Returns:
            list[str]: Список MIME типов
        """
        return [fmt.value for fmt in SupportedInputFormat]
    
    @staticmethod
    def detect_format_from_content(file_content: bytes) -> Optional[str]:
        """
        Определяет формат изображения по содержимому файла
        
        Args:
            file_content: Бинарное содержимое файла
            
        Returns:
            Optional[str]: MIME тип или None если не удалось определить
        """
        try:
            with Image.open(io.BytesIO(file_content)) as img:
                format_name = img.format
                if format_name:
                    # Мапинг формата PIL к MIME типу
                    format_to_mime = {
                        'JPEG': 'image/jpeg',
                        'PNG': 'image/png',
                        'WEBP': 'image/webp',
                        'HEIF': 'image/heic',  # HEIC и HEIF используют один MIME
                        'AVIF': 'image/avif',
                        'TIFF': 'image/tiff',
                        'BMP': 'image/bmp',
                        'GIF': 'image/gif',
                        'ICO': 'image/x-icon',
                        'JPEG2000': 'image/jp2'
                    }
                    return format_to_mime.get(format_name, f'image/{format_name.lower()}')
        except Exception as e:
            logger.warning(f"Не удалось определить формат изображения: {e}")
            
        return None
    
    @staticmethod
    def convert_to_supported_format(
        file_content: bytes, 
        original_mime_type: str
    ) -> Tuple[bytes, str]:
        """
        Конвертирует изображение в поддерживаемый формат
        
        Args:
            file_content: Бинарное содержимое файла
            original_mime_type: Оригинальный MIME тип
            
        Returns:
            Tuple[bytes, str]: Конвертированное содержимое и новый MIME тип
        """
        try:
            # Если формат уже поддерживается и не требует конвертации
            if original_mime_type in ["image/jpeg", "image/png", "image/webp"]:
                return file_content, original_mime_type
            
            # Проверяем, что формат можно конвертировать
            if original_mime_type in ImageFormatService.UNSUPPORTED_FORMATS:
                raise ValueError(f"Формат {original_mime_type} не поддерживается для конвертации")
            
            # Открываем изображение
            with Image.open(io.BytesIO(file_content)) as img:
                logger.info(f"Конвертируем {original_mime_type} ({img.format}) в JPEG")
                
                # Применяем автоповорот по EXIF
                img = ImageOps.exif_transpose(img)
                
                # Конвертируем в RGB если нужно (для JPEG)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Создаем белый фон для прозрачных изображений
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        # Для палитровых изображений
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        # Используем альфа-канал для наложения
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                
                # Сохраняем в JPEG
                output = io.BytesIO()
                img.save(
                    output,
                    format="JPEG",
                    quality=85,
                    optimize=True,
                    progressive=True
                )
                output.seek(0)
                
                converted_content = output.getvalue()
                logger.info(f"Успешно конвертировано {original_mime_type} в JPEG")
                
                return converted_content, "image/jpeg"
                
        except Exception as e:
            logger.error(f"Ошибка конвертации {original_mime_type}: {e}")
            raise ValueError(f"Не удалось конвертировать изображение: {str(e)}")
    
    @staticmethod
    def get_image_info(file_content: bytes) -> Dict[str, Any]:
        """
        Получает информацию об изображении
        
        Args:
            file_content: Бинарное содержимое файла
            
        Returns:
            Dict[str, Any]: Информация об изображении
        """
        try:
            with Image.open(io.BytesIO(file_content)) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_bytes": len(file_content),
                    "size_mb": round(len(file_content) / (1024 * 1024), 2),
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
        except Exception as e:
            logger.error(f"Ошибка получения информации об изображении: {e}")
            return {
                "size_bytes": len(file_content),
                "size_mb": round(len(file_content) / (1024 * 1024), 2),
                "error": str(e)
            }
    
    @staticmethod
    def validate_image_content(file_content: bytes, max_size_mb: int = 10) -> bool:
        """
        Валидирует содержимое изображения
        
        Args:
            file_content: Бинарное содержимое файла
            max_size_mb: Максимальный размер в МБ
            
        Returns:
            bool: True если изображение валидно
        """
        try:
            # Проверка размера файла
            size_mb = len(file_content) / (1024 * 1024)
            if size_mb > max_size_mb:
                logger.warning(f"Файл слишком большой: {size_mb:.2f} МБ")
                return False
            
            # Проверка, что файл является изображением
            with Image.open(io.BytesIO(file_content)) as img:
                # Проверяем, что можно получить размеры
                width, height = img.size
                if width == 0 or height == 0:
                    logger.warning("Изображение имеет нулевые размеры")
                    return False
                
                # Проверяем разумные ограничения размеров
                if width > 10000 or height > 10000:
                    logger.warning(f"Изображение слишком большое: {width}x{height}")
                    return False
                    
                # Проверяем, что изображение не повреждено
                img.verify()
                
                return True
                
        except Exception as e:
            logger.error(f"Ошибка валидации изображения: {e}")
            return False 