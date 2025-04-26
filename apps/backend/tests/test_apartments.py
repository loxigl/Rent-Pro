import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_get_apartments(client: TestClient):
    """Тест получения списка квартир."""
    # Выполняем GET-запрос к эндпоинту /apartments
    response = client.get("/api/v1/apartments")

    # Проверяем статус-код
    assert response.status_code == 200

    # Проверяем структуру ответа
    data = response.json()
    assert "page" in data
    assert "page_size" in data
    assert "total" in data
    assert "items" in data

    # Проверяем данные пагинации
    assert data["page"] == 1
    assert data["page_size"] == 12

    # Проверяем количество элементов (должны быть только активные квартиры)
    assert data["total"] == 2
    assert len(data["items"]) == 2

    # Проверяем содержимое первого элемента
    apartment = data["items"][0]
    assert "id" in apartment
    assert "title" in apartment
    assert "price_rub" in apartment
    assert "rooms" in apartment
    assert "floor" in apartment
    assert "area_m2" in apartment
    assert "cover_url" in apartment


def test_get_apartments_pagination(client: TestClient):
    """Тест пагинации списка квартир."""
    # Тестируем пагинацию с размером страницы 1
    response = client.get("/api/v1/apartments?page=1&page_size=1")

    # Проверяем статус-код
    assert response.status_code == 200

    # Проверяем данные пагинации
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert data["total"] == 2
    assert len(data["items"]) == 1

    # Получаем вторую страницу
    response = client.get("/api/v1/apartments?page=2&page_size=1")

    # Проверяем статус-код
    assert response.status_code == 200

    # Проверяем данные пагинации
    data = response.json()
    assert data["page"] == 2
    assert data["page_size"] == 1
    assert data["total"] == 2
    assert len(data["items"]) == 1

    # Проверяем, что на страницах разные квартиры
    response_page1 = client.get("/api/v1/apartments?page=1&page_size=1")
    response_page2 = client.get("/api/v1/apartments?page=2&page_size=1")

    apartment1 = response_page1.json()["items"][0]
    apartment2 = response_page2.json()["items"][0]

    assert apartment1["id"] != apartment2["id"]


def test_get_apartments_sorting(client: TestClient):
    """Тест сортировки списка квартир."""
    # Сортировка по цене по возрастанию
    response = client.get("/api/v1/apartments?sort=price_rub&order=asc")

    # Проверяем статус-код
    assert response.status_code == 200

    # Проверяем сортировку
    data = response.json()
    assert len(data["items"]) >= 2
    assert data["items"][0]["price_rub"] <= data["items"][1]["price_rub"]

    # Сортировка по цене по убыванию
    response = client.get("/api/v1/apartments?sort=price_rub&order=desc")

    # Проверяем статус-код
    assert response.status_code == 200

    # Проверяем сортировку
    data = response.json()
    assert len(data["items"]) >= 2
    assert data["items"][0]["price_rub"] >= data["items"][1]["price_rub"]


def test_get_apartment_detail(client: TestClient, db: Session):
    """Тест получения детальной информации о квартире."""
    # Получаем ID существующей квартиры
    apartment = db.query("Apartment").filter_by(active=True).first()
    apartment_id = apartment.id

    # Выполняем GET-запрос к эндпоинту /apartments/{id}
    response = client.get(f"/api/v1/apartments/{apartment_id}")

    # Проверяем статус-код
    assert response.status_code == 200

    # Проверяем структуру ответа
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "price_rub" in data
    assert "rooms" in data
    assert "floor" in data
    assert "area_m2" in data
    assert "address" in data
    assert "description" in data
    assert "active" in data
    assert "photos" in data
    assert "created_at" in data

    # Проверяем соответствие данных
    assert data["id"] == apartment_id
    assert data["title"] == apartment.title
    assert data["price_rub"] == apartment.price_rub
    assert data["rooms"] == apartment.rooms
    assert data["floor"] == apartment.floor
    assert data["area_m2"] == apartment.area_m2
    assert data["address"] == apartment.address
    assert data["description"] == apartment.description
    assert data["active"] == apartment.active


def test_get_apartment_not_found(client: TestClient):
    """Тест получения несуществующей квартиры."""
    # Выполняем GET-запрос с несуществующим ID
    response = client.get("/api/v1/apartments/999999")

    # Проверяем статус-код
    assert response.status_code == 404

    # Проверяем сообщение об ошибке
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Квартира не найдена"


def test_get_inactive_apartment(client: TestClient, db: Session):
    """Тест получения неактивной квартиры."""
    # Получаем ID неактивной квартиры
    apartment = db.query("Apartment").filter_by(active=False).first()
    apartment_id = apartment.id

    # Выполняем GET-запрос к эндпоинту /apartments/{id}
    response = client.get(f"/api/v1/apartments/{apartment_id}")

    # Проверяем статус-код (должен быть 404, т.к. неактивные квартиры не должны быть доступны)
    assert response.status_code == 404
