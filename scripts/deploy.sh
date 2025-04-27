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

# Функция для проверки ошибок
function check_error() {
  if [ $? -ne 0 ]; then
    echo -e "${RED}❌ $1${NC}"
    exit 1
  fi
}

# Получаем корневую директорию проекта
ROOT_DIR=$(pwd)

# Определяем режим деплоя
MODE=${1:-dev}
ENV_FILE="$ROOT_DIR/docker/.env"

log "🚀 Начинаем деплой в режиме: $MODE"

# Проверяем наличие docker
if ! command -v docker &> /dev/null; then
  echo -e "${RED}❌ Docker не установлен${NC}"
  exit 1
fi

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
  echo -e "${RED}❌ Docker Compose не установлен${NC}"
  exit 1
fi

# Проверяем наличие ENV файла
if [ ! -f "$ENV_FILE" ]; then
  log "📄 Файл .env не найден, копируем из .env.sample"
  cp "$ROOT_DIR/docker/.env.sample" "$ENV_FILE"
  check_error "Не удалось создать файл .env"
  log "✅ Файл .env создан"
fi

# Настройка конфигурации в зависимости от режима
if [ "$MODE" == "prod" ]; then
  COMPOSE_FILE="$ROOT_DIR/docker/docker-compose.prod.yml"

  # Проверяем настройку SSL для продакшена
  if grep -q "DOMAIN=rent.example.ru" "$ENV_FILE"; then
    log "⚠️ В .env файле не настроен домен. Пожалуйста, обновите DOMAIN и CERTBOT_EMAIL"
  fi

  # Создаем файлы для certbot если они отсутствуют
  mkdir -p "$ROOT_DIR/docker/certbot/conf"
  mkdir -p "$ROOT_DIR/docker/certbot/www"

  # Запускаем nginx и certbot для получения SSL сертификатов
  log "🔒 Получаем SSL сертификаты..."
  DOMAIN=$(grep DOMAIN "$ENV_FILE" | cut -d '=' -f2)
  EMAIL=$(grep CERTBOT_EMAIL "$ENV_FILE" | cut -d '=' -f2)

  # Проверяем наличие сертификатов
  if [ ! -d "$ROOT_DIR/docker/certbot/conf/live/$DOMAIN" ]; then
    log "🔄 Сертификаты не найдены, инициализируем certbot..."
    docker-compose -f "$COMPOSE_FILE" up -d nginx
    docker-compose -f "$COMPOSE_FILE" run --rm certbot certonly --webroot --webroot-path=/var/www/certbot \
      --email "$EMAIL" --agree-tos --no-eff-email -d "$DOMAIN" --force-renewal
    check_error "Не удалось получить SSL сертификаты"

    # Перезапускаем nginx для применения сертификатов
    docker-compose -f "$COMPOSE_FILE" restart nginx
  fi
else
  COMPOSE_FILE="$ROOT_DIR/docker/docker-compose.dev.yml"
fi

# Запускаем docker-compose
log "🐳 Запускаем контейнеры в режиме: $MODE"
docker-compose -f "$COMPOSE_FILE" up -d
check_error "Не удалось запустить контейнеры"

# Даем контейнерам время на запуск
log "⏳ Ожидаем запуск контейнеров..."
sleep 10

# Запускаем миграции
log "🗃️ Применяем миграции базы данных"
if [ "$MODE" == "prod" ]; then
  docker-compose -f "$COMPOSE_FILE" exec -T backend alembic upgrade head
else
  docker-compose -f "$COMPOSE_FILE" exec -T backend alembic upgrade head
fi
check_error "Не удалось применить миграции"

# Проверяем наличие данных в БД (только для dev)
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
MINIO_BUCKET=$(grep MINIO_BUCKET "$ENV_FILE" | cut -d '=' -f2)
INIT_MINIO=$(docker-compose -f "$COMPOSE_FILE" exec -T minio mkdir -p /data/$MINIO_BUCKET 2>/dev/null || echo "already exists")

# Выводим информацию о развернутом окружении
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