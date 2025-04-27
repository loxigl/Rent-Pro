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

function check_error() {
  if [ $? -ne 0 ]; then
    echo -e "${RED}❌ $1${NC}"
    exit 1
  fi
}

ROOT_DIR=$(pwd)
MODE=${1:-dev}
ENV_FILE="$ROOT_DIR/docker/.env"

log "🚀 Начинаем деплой в режиме: $MODE"

if ! command -v docker &> /dev/null; then
  echo -e "${RED}❌ Docker не установлен${NC}"
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  echo -e "${RED}❌ Docker Compose не установлен${NC}"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  log "📄 Файл .env не найден, копируем из .env.sample"
  cp "$ROOT_DIR/docker/.env.sample" "$ENV_FILE"
  check_error "Не удалось создать файл .env"
  log "✅ Файл .env создан"
fi

if [ "$MODE" == "prod" ]; then
  COMPOSE_FILE="$ROOT_DIR/docker/docker-compose.prod.yml"

  DOMAIN=$(grep DOMAIN "$ENV_FILE" | cut -d '=' -f2 | tr -d '\r')
  EMAIL=$(grep CERTBOT_EMAIL "$ENV_FILE" | cut -d '=' -f2 | tr -d '\r')

  if [[ "$DOMAIN" == "rent.example.ru" || -z "$DOMAIN" ]]; then
    log "⚠️ В .env файле не настроен домен! Пожалуйста, обновите DOMAIN и CERTBOT_EMAIL"
    exit 1
  fi
   # Проверка наличия SSL сертификатов
  if [ ! -f "$ROOT_DIR/docker/certbot/live/$DOMAIN/fullchain.pem" ]; then
    echo -e "${RED}❌ SSL сертификаты не найдены для домена $DOMAIN${NC}"
    echo -e "${RED}⚡ Пожалуйста, получите их вручную перед деплоем!${NC}"
    exit 1
  fi
  # Запуск базовых сервисов
  log "🚀 Запускаем сервисы для продакшена"
  docker-compose -f "$COMPOSE_FILE" up -d
  check_error "Не удалось запустить базовые сервисы"
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
    log "✅ В БД уже есть $APARTMENT_COUNT записей"
  fi
fi

# Инициализация MinIO
log "📦 Инициализация MinIO"
MINIO_BUCKET=$(grep MINIO_BUCKET "$ENV_FILE" | cut -d '=' -f2 | tr -d '\r')
docker-compose -f "$COMPOSE_FILE" exec -T minio mkdir -p /data/$MINIO_BUCKET 2>/dev/null || echo "already exists"

# Завершающий лог
echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}✅ Деплой успешно завершен в режиме: $MODE${NC}"
echo -e "${GREEN}=================================================${NC}"

if [ "$MODE" == "prod" ]; then
  echo -e "${YELLOW}📋 Доступные URL:${NC}"
  echo -e "${YELLOW}- Сайт: https://$DOMAIN${NC}"
  echo -e "${YELLOW}- API: https://$DOMAIN/api${NC}"
else
  echo -e "${YELLOW}📋 Доступные URL:${NC}"
  echo -e "${YELLOW}- Frontend: http://localhost:3000${NC}"
  echo -e "${YELLOW}- API: http://localhost:8000/api/v1${NC}"
  echo -e "${YELLOW}- API документация: http://localhost:8000/docs${NC}"
  echo -e "${YELLOW}- MinIO консоль: http://localhost:9001${NC}"
fi

echo -e "${YELLOW}💡 Для остановки: make stop-${MODE}${NC}"
echo -e "${GREEN}=================================================${NC}"
