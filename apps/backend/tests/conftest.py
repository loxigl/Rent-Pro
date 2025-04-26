import os
import sys
import pytest
from typing import Generator, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.database import Base, get_db
from src.main import app
from src.models.apartment import Apartment, ApartmentPhoto

# Создаем базу данных в памяти для тестирования
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Тестовые данные для квартир
test_apartments = [
    {
        "title": "Тестовая квартира 1",
        "price_rub": 1500,
        "rooms": 1,
        "floor": 3,
        "area_m2": 35.5,
        "address": "ул. Тестовая, 1",
        "description": "Тестовое описание 1",
        "active": True,
        "photos": [
            {"url": "https://example.com/test1_1.jpg", "sort_order": 0},
            {"url": "https://example.com/test1_2.jpg", "sort_order": 1},
        ]
    },
    {
        "title": "Тестовая квартира 2",
        "price_rub": 2500,
        "rooms": 2,
        "floor": 5,
        "area_m2": 56.0,
        "address": "ул. Тестовая, 2",
        "description": "Тестовое описание 2",
        "active": True,
        "photos": [
            {"url": "https://example.com/test2_1.jpg", "sort_order": 0},
        ]
    },
    {
        "title": "Неактивная квартира",
        "price_rub": 1000,
        "rooms": 1,
        "floor": 1,
        "area_m2": 30.0,
        "address": "ул. Тестовая, 3",
        "description": "Эта квартира не должна отображаться, т.к. неактивна",
        "active": False,
        "photos": []
    }
]


@pytest.fixture(scope="function")
def db():
    """
    Создает тестовую базу данных для каждого теста.
    """
    # Создаем таблицы в тестовой БД
    Base.photo_metadata.create_all(bind=engine)

    # Создаем сессию для работы с тестовой БД
    db = TestingSessionLocal()

    try:
        # Очищаем таблицы перед каждым тестом
        db.query(ApartmentPhoto).delete()
        db.query(Apartment).delete()
        db.commit()

        # Добавляем тестовые данные
        for apartment_data in test_apartments:
            photos_data = apartment_data.pop("photos")
            apartment = Apartment(**apartment_data)

            db.add(apartment)
            db.flush()  # Чтобы получить ID квартиры

            # Добавляем фотографии к квартире
            for photo_data in photos_data:
                photo = ApartmentPhoto(
                    apartment_id=apartment.id,
                    **photo_data
                )
                db.add(photo)

        db.commit()

        yield db
    finally:
        # Закрываем сессию после завершения теста
        db.close()

        # Удаляем таблицы после тестов
        Base.photo_metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Any) -> Generator:
    """
    Создает тестовый клиент FastAPI с тестовой БД.
    """

    # Переопределяем зависимость get_db, чтобы использовать тестовую БД
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Удаляем переопределение
    app.dependency_overrides = {}


@pytest.fixture
def minio_mock(monkeypatch):
    """
    Мок для сервиса MinIO.
    """

    class MinioClientMock:
        def put_object(self, *args, **kwargs):
            return True

        def presigned_get_object(self, *args, **kwargs):
            return "https://example.com/mocked-presigned-url"

        def bucket_exists(self, *args, **kwargs):
            return True

        def make_bucket(self, *args, **kwargs):
            return True

    # Заменяем Minio клиент на мок
    monkeypatch.setattr("src.services.minio_service.Minio", lambda *args, **kwargs: MinioClientMock())