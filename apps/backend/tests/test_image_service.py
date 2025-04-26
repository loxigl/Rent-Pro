import pytest
import io
from PIL import Image
import os
from src.services.image_service import ImageService, ImageSize, ImageFormat


# Создаем тестовое изображение в памяти
@pytest.fixture
def test_image():
    # Создаем RGB изображение размером 2000x1500
    img = Image.new('RGB', (2000, 1500), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


# Создаем тестовое изображение с EXIF данными
@pytest.fixture
def test_image_with_exif():
    # Здесь в реальном сценарии мы бы добавили EXIF данные
    # Для упрощения используем обычное изображение
    img = Image.new('RGB', (2000, 1500), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


def test_process_image_creates_variants(test_image):
    """Тест создания различных вариантов изображения."""
    # Обрабатываем изображение
    result = ImageService.process_image(test_image)

    # Проверяем, что созданы различные варианты
    assert len(result) > 0

    # Проверяем наличие основных вариантов
    assert "thumbnail_jpeg" in result
    assert "small_webp" in result
    assert "medium_jpeg" in result

    # Проверяем, что все значения - это байтовые строки
    for variant, content in result.items():
        assert isinstance(content, bytes)

    # Проверяем, что изображения можно открыть
    for variant, content in result.items():
        img = Image.open(io.BytesIO(content))
        assert img.mode in ('RGB', 'RGBA')


def test_resize_image_respects_max_dimensions(test_image):
    """Тест соблюдения максимальных размеров при изменении размера."""
    # Открываем изображение
    img = Image.open(io.BytesIO(test_image))

    # Проверяем различные размеры
    thumbnail = ImageService._resize_image(img, ImageSize.THUMBNAIL)
    assert max(thumbnail.size) <= 150

    small = ImageService._resize_image(img, ImageSize.SMALL)
    assert small.width <= 400

    medium = ImageService._resize_image(img, ImageSize.MEDIUM)
    assert medium.width <= 800

    large = ImageService._resize_image(img, ImageSize.LARGE)
    assert large.width <= 1200

    original = ImageService._resize_image(img, ImageSize.ORIGINAL)
    assert original.width <= 1920 and original.height <= 1920


def test_create_thumbnail_creates_square_image(test_image):
    """Тест создания квадратного изображения для thumbnail."""
    # Открываем изображение
    img = Image.open(io.BytesIO(test_image))

    # Создаем thumbnail
    thumbnail = ImageService._create_thumbnail(img, (150, 150))

    # Проверяем размеры
    assert thumbnail.width == 150
    assert thumbnail.height == 150


def test_get_image_info_returns_correct_data(test_image):
    """Тест получения информации об изображении."""
    # Получаем информацию
    info = ImageService.get_image_info(test_image)

    # Проверяем наличие основных полей
    assert "width" in info
    assert "height" in info
    assert "format" in info
    assert "mode" in info

    # Проверяем значения
    assert info["width"] == 2000
    assert info["height"] == 1500
    assert info["format"] == "JPEG"
    assert info["mode"] == "RGB"


def test_generate_image_filename():
    """Тест генерации имени файла для изображения."""
    # Генерируем имя файла без варианта
    filename = ImageService.generate_image_filename(123)
    assert filename.startswith("apartments/123/")
    assert filename.endswith(".jpg")

    # Генерируем имя файла с вариантом JPEG
    filename = ImageService.generate_image_filename(123, "small_jpeg")
    assert filename.startswith("apartments/123/")
    assert filename.endswith("_small_jpeg.jpg")

    # Генерируем имя файла с вариантом WebP
    filename = ImageService.generate_image_filename(123, "medium_webp")
    assert filename.startswith("apartments/123/")
    assert filename.endswith("_medium_webp.webp")