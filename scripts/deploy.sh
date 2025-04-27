#!/bin/bash
set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция вывода сообщений
function log() {
  echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

function success() {
  echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

function error() {
  echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

function check_error() {
  if [ $? -ne 0 ]; then
    error "❌ $1"
    exit 1
  fi
}

ROOT_DIR=$(pwd)
MODE=${1:-dev}
ENV_FILE="$ROOT_DIR/docker/.env"

log "🚀 Начинаем деплой в режиме: $MODE"

# Проверка наличия Docker и Docker Compose
if ! command -v docker &> /dev/null; then
  error "❌ Docker не установлен"
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  error "❌ Docker Compose не установлен"
  exit 1
fi

# Проверка наличия .env файла
if [ ! -f "$ENV_FILE" ]; then
  log "📄 Файл .env не найден, копируем из .env.sample"
  cp "$ROOT_DIR/docker/.env.sample" "$ENV_FILE"
  check_error "Не удалось создать файл .env"
  success "✅ Файл .env создан"
fi

# Определение файла docker-compose
if [ "$MODE" == "prod" ]; then
  COMPOSE_FILE="$ROOT_DIR/docker/docker-compose.prod.yml"

  # Загружаем переменные из .env
  source $ENV_FILE

  # Проверка настройки домена
  DOMAIN=${DOMAIN:-"example.com"}
  if [[ "$DOMAIN" == "example.com" || -z "$DOMAIN" ]]; then
    error "⚠️ В .env файле не настроен домен! Пожалуйста, обновите DOMAIN и CERTBOT_EMAIL"
    exit 1
  fi

  # Проверка наличия SSL сертификатов
  if [ ! -d "$ROOT_DIR/docker/certbot/conf/live/$DOMAIN" ]; then
    log "🔒 SSL сертификаты не найдены для домена $DOMAIN"
    log "🔒 Запуск скрипта получения SSL сертификатов..."

    # Проверяем, указан ли CERTBOT_EMAIL
    if [[ -z "$CERTBOT_EMAIL" ]]; then
      error "❌ Не указан CERTBOT_EMAIL в .env файле"
      exit 1
    fi

    # Запускаем скрипт настройки SSL
    bash "$ROOT_DIR/scripts/setup-ssl.sh" "$DOMAIN" "$CERTBOT_EMAIL"
    check_error "Не удалось получить SSL сертификаты"
  fi

  # Поочередное поднятие сервисов для продакшена

  # 1. Поднимаем базовые сервисы (DB, Redis, MinIO)
  log "🚀 Запускаем базовые сервисы (DB, Redis, MinIO)..."
  docker-compose -f "$COMPOSE_FILE" up -d db redis minio
  check_error "Не удалось запустить базовые сервисы"

  # Ждем, пока базовые сервисы будут готовы
  log "⏳ Ожидание готовности базовых сервисов..."
  sleep 10

  # 2. Поднимаем бэкенд
  log "🚀 Запускаем бэкенд и worker..."
  docker-compose -f "$COMPOSE_FILE" up -d backend celery_worker
  check_error "Не удалось запустить бэкенд"

  # Ждем, пока бэкенд будет готов
  log "⏳ Ожидание готовности бэкенда..."
  sleep 10

  # 3. Поднимаем фронтенд
  log "🚀 Запускаем фронтенд..."
  docker-compose -f "$COMPOSE_FILE" up -d frontend
  check_error "Не удалось запустить фронтенд"

  # Ждем, пока фронтенд будет готов
  log "⏳ Ожидание готовности фронтенда..."
  sleep 10

  # 4. Запускаем Nginx и Certbot
  log "🚀 Запускаем Nginx и Certbot..."
  docker-compose -f "$COMPOSE_FILE" up -d nginx certbot
  check_error "Не удалось запустить Nginx и Certbot"
else
  COMPOSE_FILE="$ROOT_DIR/docker/docker-compose.dev.yml"
  log "🐳 Запускаем все контейнеры в режиме $MODE"
  docker-compose -f "$COMPOSE_FILE" up -d
  check_error "Не удалось запустить контейнеры"
fi

# Миграции базы данных
log "🗃️ Применяем миграции базы данных"
docker-compose -f "$COMPOSE_FILE" exec -T backend alembic -c alembic.ini upgrade head
check_error "Не удалось применить миграции"

# Для dev режима наполнение тестовыми данными
if [ "$MODE" == "dev" ]; then
  log "🧪 Проверяем наличие тестовых данных"
  APARTMENT_COUNT=$(docker-compose -f "$COMPOSE_FILE" exec -T db psql -U postgres -d avitorentpro -c "SELECT COUNT(*) FROM apartment;" -t 2>/dev/null || echo "0")
  APARTMENT_COUNT=$(echo $APARTMENT_COUNT | tr -d ' ')

  if [[ $APARTMENT_COUNT == "0" || $APARTMENT_COUNT == *"does not exist"* ]]; then
    log "🧪 Заполняем БД тестовыми данными"
    docker-compose -f "$COMPOSE_FILE" exec -T backend python -m scripts.seed_data
    check_error "Не удалось заполнить БД тестовыми данными"
  else
    success "✅ В БД уже есть $APARTMENT_COUNT записей"
  fi
fi

# Проверка работоспособности сервисов
log "🔍 Проверка работоспособности сервисов..."

if [ "$MODE" == "prod" ]; then
  # В продакшене проверяем доступность через Nginx
  log "🔍 Проверка доступности сервисов через Nginx..."
  if command -v curl &> /dev/null; then
    # Проверка HTTP (должен быть редирект на HTTPS)
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN/)
    if [[ "$HTTP_STATUS" == "301" || "$HTTP_STATUS" == "302" ]]; then
      success "✅ HTTP редирект работает корректно ($HTTP_STATUS)"
    else
      log "⚠️ HTTP редирект не работает (статус: $HTTP_STATUS)"
    fi

    # Проверка HTTPS (может не сработать, если DNS не настроен на локальной машине)
    if curl -k -s https://$DOMAIN/ > /dev/null; then
      success "✅ HTTPS доступ работает корректно"
    else
      log "⚠️ HTTPS доступ не работает. Проверьте настройку DNS для домена $DOMAIN"
    fi
  else
    log "⚠️ curl не установлен, пропускаем проверку доступности"
  fi
else
  # В режиме разработки проверяем прямой доступ к сервисам
  if command -v curl &> /dev/null; then
    if curl -s http://localhost:8000/api/v1 > /dev/null; then
      success "✅ Бэкенд API доступен"
    else
      log "⚠️ Бэкенд API недоступен"
    fi

    if curl -s http://localhost:3000 > /dev/null; then
      success "✅ Фронтенд доступен"
    else
      log "⚠️ Фронтенд недоступен"
    fi
  else
    log "⚠️ curl не установлен, пропускаем проверку доступности"
  fi
fi

# Завершающий лог
success "================================================="
success "✅ Деплой успешно завершен в режиме: $MODE"
success "================================================="

if [ "$MODE" == "prod" ]; then
  log "📋 Доступные URL:"
  log "- Сайт: https://$DOMAIN"
  log "- API: https://$DOMAIN/api"
else
  log "📋 Доступные URL:"
  log "- Frontend: http://localhost:3000"
  log "- API: http://localhost:8000/api/v1"
  log "- API документация: http://localhost:8000/docs"
  log "- MinIO консоль: http://localhost:9001"
fi

log "💡 Для остановки: make down-${MODE}"
success "================================================="