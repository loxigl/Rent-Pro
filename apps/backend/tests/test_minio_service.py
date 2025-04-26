import pytest
import io
from unittest.mock import patch, MagicMock
from PIL import Image
from minio.error import S3Error

from src.services.minio_service import MinioService
from src.services.image_service import ImageService


# Фикстура для создания тестового изображения
@pytest.fixture
def test_image():
    img = Image.new('RGB', (800, 600), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


# Фикстура для мока MinIO клиента
@pytest.fixture
def minio_client_mock():
    with patch('src.services.minio_service.Minio') as mock:
        client = MagicMock()
        mock.return_value = client
        client.bucket_exists.return_value = True
        yield client


# Тест создания экземпляра MinioService
def test_minio_service_init(minio_client_mock):
    service = MinioService()
    assert service.client == minio_client_mock
    assert service.bucket_name is not None


# Тест проверки и создания бакета
def test_ensure_bucket_exists_when_bucket_exists(minio_client_mock):
    service = MinioService()
    service._ensure_bucket_exists()
    minio_client_mock.bucket_exists.assert_called_once()
    minio_client_mock.make_bucket.assert_not_called()


def test_ensure_bucket_exists_when_bucket_does_not_exist(minio_client_mock):
    minio_client_mock.bucket_exists.return_value = False
    service = MinioService()
    service._ensure_bucket_exists()
    minio_client_mock.bucket_exists.assert_called_once()
    minio_client_mock.make_bucket.assert_called_once()
    minio_client_mock.set_bucket_policy.assert_called_once()


# Тест загрузки изображения
@pytest.mark.parametrize("apartment_id", [1, 2, 3])
def test_upload_image(minio_client_mock, test_image, apartment_id):
    # Мокаем ImageService.process_image для возврата заранее определенных вариантов
    with patch('src.services.image_service.ImageService.process_image') as mock_process:
        with patch('src.services.image_service.ImageService.get_image_info') as mock_info:
            # Настраиваем моки
            mock_process.return_value = {
                "thumbnail_jpeg": b"thumbnail_jpeg_data",
                "small_webp": b"small_webp_data",
                "medium_jpeg": b"medium_jpeg_data",
            }
            mock_info.return_value = {
                "width": 800,
                "height": 600,
                "format": "JPEG",
                "mode": "RGB"
            }

            # Вызываем метод загрузки
            service = MinioService()
            result = service.upload_image(test_image, apartment_id)

            # Проверяем, что process_image был вызван с правильными параметрами
            mock_process.assert_called_once_with(test_image)

            # Проверяем, что get_image_info был вызван с правильными параметрами
            mock_info.assert_called_once_with(test_image)

            # Проверяем, что put_object был вызван для каждого варианта
            assert minio_client_mock.put_object.call_count == 3

            # Проверяем результат
            assert isinstance(result, dict)
            assert len(result) == 3
            assert all(isinstance(url, str) for url in result.values())


# Тест получения изображений квартиры
def test_get_apartment_images(minio_client_mock):
    # Настраиваем мок для list_objects
    object1 = MagicMock()
    object1.object_name = f"apartments/1/abc123_small_webp.webp"

    object2 = MagicMock()
    object2.object_name = f"apartments/1/abc123_medium_jpeg.jpg"

    object3 = MagicMock()
    object3.object_name = f"apartments/1/def456_original_jpeg.jpg"

    minio_client_mock.list_objects.return_value = [object1, object2, object3]

    # Вызываем метод
    service = MinioService()
    result = service.get_apartment_images(1)

    # Проверяем результат
    assert isinstance(result, dict)
    assert len(result) == 2  # два уникальных image_id
    assert "abc123" in result
    assert "def456" in result
    assert len(result["abc123"]) == 2  # два варианта для abc123
    assert len(result["def456"]) == 1  # один вариант для def456


# Тест генерации подписанного URL
def test_generate_presigned_url(minio_client_mock):
    # Настраиваем мок
    minio_client_mock.presigned_get_object.return_value = "https://example.com/presigned-url"

    # Вызываем метод
    service = MinioService()
    result = service.generate_presigned_url("test-object", 3600)

    # Проверяем результат
    assert result == "https://example.com/presigned-url"
    minio_client_mock.presigned_get_object.assert_called_once()


# Тест удаления изображения
def test_delete_image(minio_client_mock):
    # Настраиваем мок для list_objects
    object1 = MagicMock()
    object1.object_name = f"apartments/1/abc123_small_webp.webp"

    object2 = MagicMock()
    object2.object_name = f"apartments/1/abc123_medium_jpeg.jpg"

    minio_client_mock.list_objects.return_value = [object1, object2]

    # Вызываем метод
    service = MinioService()
    result = service.delete_image(1, "abc123")

    # Проверяем результат
    assert result is True
    assert minio_client_mock.remove_object.call_count == 2


# Тест обработки ошибок S3
def test_error_handling(minio_client_mock):
    # Настраиваем мок для вызова исключения
    minio_client_mock.bucket_exists.side_effect = S3Error("Test error")

    # Проверяем, что исключение прокидывается
    service = MinioService()
    with pytest.raises(S3Error):
        service._ensure_bucket_exists()