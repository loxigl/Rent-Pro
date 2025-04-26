# Makefile для удобства запуска команд в проекте AvitoRentPro

.PHONY: setup dev test down clean rebuild deploy help minio-init frontend

# Переменные
DOCKER_COMPOSE_DEV = docker/docker-compose.dev.yml
DOCKER_COMPOSE_PROD = docker/docker-compose.prod.yml

# Помощь
help:
	@echo "Доступные команды:"
	@echo "  make setup     - Инициализация проекта (установка зависимостей, создание .env файлов)"
	@echo "  make dev       - Запуск окружения разработки (бэкенд и контейнеры)"
	@echo "  make frontend  - Запуск frontend dev-сервера"
	@echo "  make test      - Запуск всех тестов"
	@echo "  make down      - Остановка контейнеров"
	@echo "  make clean     - Удаление всех контейнеров и данных (postgres, minio, redis)"
	@echo "  make rebuild   - Пересборка контейнеров"
	@echo "  make deploy    - Деплой на продакшен"
	@echo "  make minio-init - Инициализация MinIO (создание бакета и настройка прав доступа)"

# Инициализация проекта
setup:
	@bash apps/frontend/scripts/setup.sh

# Запуск окружения разработки
dev:
	@bash apps/backend/scripts/dev.sh

# Запуск frontend dev-сервера
frontend:
	@cd apps/frontend && npm run dev

# Запуск тестов
test:
	@bash apps/backend/scripts/run_test.sh

# Остановка контейнеров
down:
	docker-compose -f $(DOCKER_COMPOSE_DEV) down

# Полная очистка
clean:
	docker-compose -f $(DOCKER_COMPOSE_DEV) down -v
	@echo "Все контейнеры и данные удалены"

# Пересборка контейнеров
rebuild:
	docker-compose -f $(DOCKER_COMPOSE_DEV) build
	@echo "Контейнеры пересобраны"

# Деплой на продакшен
deploy:
	@echo "Выполняется деплой на продакшен..."
	@cd docker && docker-compose -f $(DOCKER_COMPOSE_PROD) up -d
	@echo "Деплой завершен"

# Инициализация MinIO
minio-init:
	@bash apps/backend/scripts/init-minio.sh

# Значение по умолчанию
default: help