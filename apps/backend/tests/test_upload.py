import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch


def test_upload_photo_success(client: TestClient, db: Session, minio_mock):
    """Тест успешной загрузки фотографии."""
    # Получаем ID существующей квартиры
    apartment = db.query("Apartment").filter_by(active=True).first()
    apartment_id = apartment.id

    # Создаем тестовое изображение
    test_image = io.BytesIO(b"test image content")
    test_image.name = "test.jpg"

    # Подготавливаем файл для загрузки
    files = {"file": ("test.jpg", test_image, "image/jpeg")}
    data = {"apartment_id": str(apartment_id)}

    # Мокаем вызов Celery task
    with patch("src.api.apartments.process_image") as mock_process_image:
        # Настраиваем мок для возврата URL
        mock_task = mock_process_image.delay.return_value
        mock_task.get.return_value = "https://example.com/test_uploaded.jpg"

        # Выполняем POST-запрос к эндпоинту /admin/upload
        response = client.post("/api/v1/admin/upload", files=files, data=data)

        # Проверяем статус-код
        assert response.status_code == 201

        # Проверяем структуру ответа
        result = response.json()
        assert "id" in result
        assert "url" in result
        assert "apartment_id" in result
        assert "sort_order" in result

        # Проверяем данные
        assert result["url"] == "https://example.com/test_uploaded.jpg"
        assert result["apartment_id"] == apartment_id

        # Проверяем, что Celery task был вызван
        mock_process_image.delay.assert_called_once()


def test_upload_photo_invalid_format(client: TestClient, db: Session):
    """Тест загрузки файла неверного формата."""
    # Получаем ID существующей квартиры
    apartment = db.query("Apartment").filter_by(active=True).first()
    apartment_id = apartment.id

    # Создаем тестовый файл неверного формата
    test_file = io.BytesIO(b"test text content")
    test_file.name = "test.txt"

    # Подготавливаем файл для загрузки
    files = {"file": ("test.txt", test_file, "text/plain")}
    data = {"apartment_id": str(apartment_id)}

    # Выполняем POST-запрос к эндпоинту /admin/upload
    response = client.post("/api/v1/admin/upload", files=files, data=data)

    # Проверяем статус-код
    assert response.status_code == 400

    # Проверяем сообщение об ошибке
    result = response.json()
    assert "detail" in result
    assert "Поддерживаются только JPEG и PNG изображения" in result["detail"]


def test_upload_photo_apartment_not_found(client: TestClient):
    """Тест загрузки фотографии для несуществующей квартиры."""
    # Создаем тестовое изображение
    test_image = io.BytesIO(b"test image content")
    test_image.name = "test.jpg"

    # Подготавливаем файл для загрузки
    files = {"file": ("test.jpg", test_image, "image/jpeg")}
    data = {"apartment_id": "999999"}  # Несуществующий ID

    # Выполняем POST-запрос к эндпоинту /admin/upload
    response = client.post("/api/v1/admin/upload", files=files, data=data)

    # Проверяем статус-код
    assert response.status_code == 404

    # Проверяем сообщение об ошибке
    result = response.json()
    assert "detail" in result
    assert "Квартира не найдена" in result["detail"]


def test_upload_photo_too_large(client: TestClient, db: Session, monkeypatch):
    """Тест загрузки слишком большого файла."""
    # Получаем ID существующей квартиры
    apartment = db.query("Apartment").filter_by(active=True).first()
    apartment_id = apartment.id

    # Создаем тестовое изображение с размером чуть больше максимально допустимого
    # Устанавливаем максимальный размер в 1 КБ для теста
    monkeypatch.setattr("src.config.settings.settings.MAX_IMAGE_SIZE_MB", 0.001)  # 1 KB

    # Создаем изображение размером 2 КБ
    test_image = io.BytesIO(b"a" * 2 * 1024)
    test_image.name = "test.jpg"

    # Подготавливаем файл для загрузки
    files = {"file": ("test.jpg", test_image, "image/jpeg")}
    data = {"apartment_id": str(apartment_id)}

    # Выполняем POST-запрос к эндпоинту /admin/upload
    response = client.post("/api/v1/admin/upload", files=files, data=data)

    # Проверяем статус-код
    assert response.status_code == 400

    # Проверяем сообщение об ошибке
    result = response.json()
    assert "detail" in result
    assert "Размер файла превышает" in result["detail"]
