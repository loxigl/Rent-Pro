# Makefile для проекта AvitoRentPro

.PHONY: setup dev prod frontend test down-dev down-prod clean-dev clean-prod rebuild help logs-dev logs-prod

# Переменные
DOCKER_COMPOSE_DEV = docker/docker-compose.dev.yml
DOCKER_COMPOSE_PROD = docker/docker-compose.prod.yml
DEPLOY_SCRIPT = scripts/deploy.sh

# Помощь
help:
	@echo "Доступные команды:"
	@echo "  • Разработка:"
	@echo "    make setup      - Инициализация проекта"
	@echo "    make dev        - Деплой окружения разработки"
	@echo "    make frontend   - Запуск только frontend dev-сервера"
	@echo "    make down-dev   - Остановка контейнеров разработки"
	@echo "    make logs-dev   - Просмотр логов разработки"
	@echo "    make clean-dev  - Удаление всех контейнеров и данных разработки"
	@echo "  • Продакшен:"
	@echo "    make prod           - Деплой продакшен-окружения"
	@echo "    make rebuild-prod   - Пересборка всех продакшен-контейнеров"
	@echo "    make rebuild-frontend - Пересборка только frontend в продакшене"
	@echo "    make rebuild-backend  - Пересборка только backend в продакшене"
	@echo "    make down-prod  - Остановка продакшен-контейнеров"
	@echo "    make logs-prod  - Просмотр логов продакшена"
	@echo "    make clean-prod - Удаление всех продакшен-контейнеров и данных"
	@echo "  • Общие команды:"
	@echo "    make test       - Запуск всех тестов"
	@echo "    make rebuild    - Пересборка контейнеров разработки"

# Инициализация проекта
setup:
	@bash scripts/setup.sh

# Деплой окружения разработки
dev:
	@bash $(DEPLOY_SCRIPT) dev

# Деплой продакшен-окружения
prod:
	@bash $(DEPLOY_SCRIPT) prod

# Запуск только frontend dev-сервера
frontend:
	@cd apps/frontend && npm run dev

# Остановка контейнеров разработки
down-dev:
	docker-compose -f $(DOCKER_COMPOSE_DEV) down

# Остановка продакшен-контейнеров
down-prod:
	docker-compose -f $(DOCKER_COMPOSE_PROD) down

# Просмотр логов разработки
logs-dev:
	docker-compose -f $(DOCKER_COMPOSE_DEV) logs -f

# Просмотр логов продакшена
logs-prod:
	docker-compose -f $(DOCKER_COMPOSE_PROD) logs -f

# Тесты
test:
	@bash scripts/test.sh

# Полная очистка dev
clean-dev:
	docker-compose -f $(DOCKER_COMPOSE_DEV) down -v
	@echo "Все контейнеры и данные разработки удалены"

# Полная очистка prod
clean-prod:
	docker-compose -f $(DOCKER_COMPOSE_PROD) down -v
	@echo "Все продакшен-контейнеры и данные удалены"

# Пересборка контейнеров
rebuild:
	docker-compose -f $(DOCKER_COMPOSE_DEV) build
	@echo "Контейнеры пересобраны"

# Пересборка всех продакшн-контейнеров
rebuild-prod:
	docker-compose -f $(DOCKER_COMPOSE_PROD) build
	docker-compose -f $(DOCKER_COMPOSE_PROD) up -d --no-deps
	@echo "Все продакшн-контейнеры пересобраны и запущены"

# Пересборка только frontend в продакшн
rebuild-frontend:
	docker-compose -f $(DOCKER_COMPOSE_PROD) build frontend
	docker-compose -f $(DOCKER_COMPOSE_PROD) up -d --no-deps frontend
	@echo "Frontend в продакшн пересобран и запущен"

# Пересборка только backend в продакшн
rebuild-backend:
	docker-compose -f $(DOCKER_COMPOSE_PROD) build backend
	docker-compose -f $(DOCKER_COMPOSE_PROD) up -d --no-deps backend
	docker-compose -f $(DOCKER_COMPOSE_PROD) build celery_worker
	docker-compose -f $(DOCKER_COMPOSE_PROD) up -d --no-deps celery_worker
	@echo "Backend в продакшн пересобран и запущен"
# Значение по умолчанию
default: help