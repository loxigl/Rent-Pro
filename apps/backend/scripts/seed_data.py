"""
Скрипт для заполнения базы данных тестовыми данными.
Запуск: python -m scripts.seed_data
"""

import sys
import os
import logging
from sqlalchemy.orm import Session
from datetime import datetime

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.database import SessionLocal, engine, Base
from src.models.apartment import Apartment, ApartmentPhoto

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Тестовые данные для квартир
test_apartments = [
    {
        "title": "Уютная 1-к квартира в центре",
        "price_rub": 1500,
        "rooms": 1,
        "floor": 3,
        "area_m2": 35.5,
        "address": "ул. Ленина, 15",
        "description": """
# Уютная квартира в центре города

Предлагаем вашему вниманию комфортную квартиру в самом центре Невинномысска.

## Особенности:
- Свежий ремонт
- Полностью укомплектованная кухня
- Стиральная машина и кондиционер
- Высокоскоростной интернет

Рядом находятся магазины, кафе и остановки общественного транспорта. 
До парка всего 5 минут пешком.
        """,
        "active": True,
        "photos": [
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+1-1", "sort_order": 0},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+1-2", "sort_order": 1},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+1-3", "sort_order": 2},
        ]
    },
    {
        "title": "Просторная 2-к с видом на реку",
        "price_rub": 2500,
        "rooms": 2,
        "floor": 5,
        "area_m2": 56.0,
        "address": "ул. Набережная, 23",
        "description": """
# Просторная квартира с видом на реку

Шикарная 2-комнатная квартира с панорамным видом на реку Кубань.

## Информация о квартире:
- Просторная гостиная и спальня
- Отдельная кухня с современной техникой
- Балкон с живописным видом
- Подземная парковка для гостей

Рядом благоустроенная набережная для прогулок и утренних пробежек.
        """,
        "active": True,
        "photos": [
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+2-1", "sort_order": 0},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+2-2", "sort_order": 1},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+2-3", "sort_order": 2},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+2-4", "sort_order": 3},
        ]
    },
    {
        "title": "Семейная 3-к рядом с парком",
        "price_rub": 3500,
        "rooms": 3,
        "floor": 2,
        "area_m2": 78.5,
        "address": "ул. Парковая, 7",
        "description": """
# Идеальная квартира для семейного отдыха

Просторная 3-комнатная квартира в тихом районе рядом с городским парком.

## Планировка:
- Большая гостиная с выходом на лоджию
- Две раздельные спальни
- Кухня-столовая
- Два санузла
- Гардеробная комната

Отличный вариант для семьи с детьми или компании друзей.
        """,
        "active": True,
        "photos": [
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+3-1", "sort_order": 0},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+3-2", "sort_order": 1},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+3-3", "sort_order": 2},
        ]
    },
    {
        "title": "Студия в современном стиле",
        "price_rub": 1200,
        "rooms": 1,
        "floor": 9,
        "area_m2": 28.0,
        "address": "пр. Молодежный, 42",
        "description": """
# Стильная студия для современных людей

Компактная и функциональная квартира-студия с современным ремонтом.

## Преимущества:
- Эргономичное использование пространства
- Полностью оборудованная кухонная зона
- Функциональная мебель-трансформер
- Система умный дом
- Высокий этаж с хорошим видом

Идеально подходит для командировок или романтического уикенда.
        """,
        "active": True,
        "photos": [
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+4-1", "sort_order": 0},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+4-2", "sort_order": 1},
        ]
    },
    {
        "title": "Элитная 2-к в новостройке",
        "price_rub": 3000,
        "rooms": 2,
        "floor": 12,
        "area_m2": 68.5,
        "address": "ул. Строителей, 12",
        "description": """
# Элитная квартира в новом комплексе

Эксклюзивная квартира с дизайнерским ремонтом в недавно построенном жилом комплексе.

## Характеристики:
- Два отдельных санузла
- Просторная лоджия с панорамным остеклением
- Система климат-контроля
- Дизайнерская мебель и техника премиум-класса
- Охраняемая территория и подземный паркинг

Дополнительно предоставляется доступ к инфраструктуре комплекса: спортзал, сауна, бассейн.
        """,
        "active": True,
        "photos": [
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+5-1", "sort_order": 0},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+5-2", "sort_order": 1},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+5-3", "sort_order": 2},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+5-4", "sort_order": 3},
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Apartment+5-5", "sort_order": 4},
        ]
    },
    # Неактивная квартира (не должна отображаться в каталоге)
    {
        "title": "Скрытая квартира (не активна)",
        "price_rub": 1000,
        "rooms": 1,
        "floor": 1,
        "area_m2": 30.0,
        "address": "ул. Тестовая, 1",
        "description": "Эта квартира не должна отображаться в каталоге, так как active = False",
        "active": False,
        "photos": [
            {"url": "https://via.placeholder.com/1920x1080.jpg?text=Hidden", "sort_order": 0},
        ]
    }
]


def seed_database():
    """Заполняет базу данных тестовыми данными."""
    db = SessionLocal()
    try:
        # Создаем таблицы, если они еще не существуют
        Base.metadata.create_all(bind=engine)

        # Проверяем, есть ли уже данные в таблицах
        if db.query(Apartment).count() > 0:
            logger.info("База данных уже содержит записи, очищаем...")
            db.query(ApartmentPhoto).delete()
            db.query(Apartment).delete()
            db.commit()

        logger.info("Начинаем заполнение базы данных тестовыми данными...")

        # Добавляем квартиры и их фотографии
        for apartment_data in test_apartments:
            # Создаем квартиру
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

            logger.info(f"Добавлена квартира: {apartment.title}")

        db.commit()
        logger.info("База данных успешно заполнена!")

    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при заполнении базы данных: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()