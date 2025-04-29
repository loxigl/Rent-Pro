from locust import HttpUser, task, between, constant
import random
import json


class ApartmentUser(HttpUser):
    """
    Пользователь для нагрузочного тестирования Kvartiry26.

    Эмулирует поведение пользователя, который просматривает каталог квартир,
    открывает детальные страницы и взаимодействует с API.
    """

    # Задержка между задачами для имитации поведения реального пользователя
    wait_time = between(1, 5)

    # Сохраняем ID квартир для повторного использования
    apartment_ids = []

    def on_start(self):
        """
        Метод, выполняемый перед началом тестирования для конкретного пользователя.
        Получает список ID квартир для последующих тестов.
        """
        # Запрашиваем список квартир через API
        response = self.client.get("/api/v1/apartments?page=1&page_size=40")

        if response.status_code == 200:
            data = response.json()
            self.apartment_ids = [apartment["id"] for apartment in data["items"]]

        # Если не удалось получить ID, используем тестовые значения
        if not self.apartment_ids:
            self.apartment_ids = [1, 2, 3]

    @task(5)
    def view_catalog(self):
        """
        Задача: просмотр страницы каталога.
        Вес 5: выполняется чаще других задач.
        """
        # Тестируем разные варианты страниц и сортировки
        page = random.randint(1, 3)
        sort_options = ["created_at", "price_rub"]
        order_options = ["asc", "desc"]

        sort = random.choice(sort_options)
        order = random.choice(order_options)

        # Сначала делаем запрос к API
        self.client.get(f"/api/v1/apartments?page={page}&page_size=12&sort={sort}&order={order}")

        # Затем просматриваем HTML-страницу каталога
        self.client.get(f"/catalog?page={page}&sort={sort}&order={order}")

    @task(3)
    def view_apartment_details(self):
        """
        Задача: просмотр детальной страницы квартиры.
        Вес 3: выполняется реже, чем просмотр каталога.
        """
        if self.apartment_ids:
            apartment_id = random.choice(self.apartment_ids)

            # Сначала делаем запрос к API
            self.client.get(f"/api/v1/apartments/{apartment_id}")

            # Затем просматриваем HTML-страницу с деталями
            self.client.get(f"/apartment/{apartment_id}")

    @task(1)
    def view_homepage(self):
        """
        Задача: просмотр главной страницы.
        Вес 1: выполняется реже других задач.
        """
        self.client.get("/")


class ApiLoadTest(HttpUser):
    """
    Пользователь для нагрузочного тестирования API.

    Эмулирует интенсивное использование только API-эндпоинтов.
    """

    # Постоянное время ожидания для имитации высокой нагрузки
    wait_time = constant(0.1)

    # Сохраняем ID квартир для повторного использования
    apartment_ids = []

    def on_start(self):
        """
        Метод, выполняемый перед началом тестирования для конкретного пользователя.
        Получает список ID квартир для последующих тестов.
        """
        # Запрашиваем список квартир через API
        response = self.client.get("/api/v1/apartments?page=1&page_size=40")

        if response.status_code == 200:
            data = response.json()
            self.apartment_ids = [apartment["id"] for apartment in data["items"]]

        # Если не удалось получить ID, используем тестовые значения
        if not self.apartment_ids:
            self.apartment_ids = [1, 2, 3]

    @task(5)
    def api_get_apartments(self):
        """
        Задача: запрос списка квартир через API.
        Вес 5: выполняется чаще других задач.
        """
        page = random.randint(1, 3)
        sort_options = ["created_at", "price_rub"]
        order_options = ["asc", "desc"]

        sort = random.choice(sort_options)
        order = random.choice(order_options)

        self.client.get(f"/api/v1/apartments?page={page}&page_size=12&sort={sort}&order={order}")

    @task(3)
    def api_get_apartment_detail(self):
        """
        Задача: запрос детальной информации о квартире через API.
        Вес 3: выполняется реже, чем запрос списка.
        """
        if self.apartment_ids:
            apartment_id = random.choice(self.apartment_ids)
            self.client.get(f"/api/v1/apartments/{apartment_id}")

# Запуск тестов:
# locust -f locustfile.py --host=http://localhost:3000
