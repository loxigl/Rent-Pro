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

  # 3. Запускаем временный прокси к бэкенду
  log "🚀 Запускаем временный прокси к бэкенду..."

  # Определяем сеть Docker
  DOCKER_NETWORK=$(docker network ls --filter "name=avitorentpro" --format "{{.Name}}" | head -n 1)
  log "✅ Найдена сеть Docker: $DOCKER_NETWORK"

  # Находим имя контейнера бэкенда
  BACKEND_CONTAINER=$(docker ps --filter "name=backend" --format "{{.Names}}" | head -n 1)
  log "✅ Найден контейнер бэкенда: $BACKEND_CONTAINER"

  # Запускаем временный прокси
  log "🚀 Запускаем временный прокси с доступом к контейнеру $BACKEND_CONTAINER в сети $DOCKER_NETWORK"
  PROXY_ID=$(docker run -d --network $DOCKER_NETWORK --name temp-proxy-for-build nginx:alpine)

  # Настраиваем прокси для перенаправления на бэкенд
  docker exec $PROXY_ID sh -c "echo 'server { listen 80; location /api/ { proxy_pass http://$BACKEND_CONTAINER:8000/api/; }}' > /etc/nginx/conf.d/default.conf && nginx -s reload"

  log "⏳ Ожидание готовности прокси..."
  sleep 1

  # Проверяем доступность API через прокси
  log "🔍 Проверка доступности API..."
  if docker exec $PROXY_ID curl -s http://localhost/api/api/v1/apartments?page_size=1 > /dev/null; then
    log "✅ API успешно доступен через прокси"
  else
    log "⚠️ API не доступен через прокси, проверяем прямую доступность"
    if docker exec $PROXY_ID curl -s http://$BACKEND_CONTAINER:8000/api/api/v1/apartments?page_size=1 > /dev/null; then
      log "✅ API доступен напрямую"
    else
      log "⚠️ API недоступен"
    fi
  fi

  # Предварительная проверка API для генерации sitemap
  log "🔍 Предварительная проверка API для генерации sitemap..."
  SITEMAP_DATA_DIR="/var/www/avitorentpro/apps/frontend/public"
  mkdir -p $SITEMAP_DATA_DIR

  if curl -s http://localhost:8000/api/api/v1/apartments?page_size=1 > /dev/null || docker exec $PROXY_ID curl -s http://$BACKEND_CONTAINER:8000/api/api/v1/apartments?page_size=1 > /dev/null; then
    log "✅ Успешно получены данные для sitemap"
    # Сохраняем данные для sitemap
    API_DATA=$(docker exec $PROXY_ID curl -s http://$BACKEND_CONTAINER:8000/api/api/v1/apartments?page_size=40)
    echo "$API_DATA" > $SITEMAP_DATA_DIR/sitemap-data.json
    log "📦 Данные для sitemap сохранены в файл: $SITEMAP_DATA_DIR/sitemap-data.json"
  else
    log "⚠️ API недоступен для генерации sitemap"
    mkdir -p $SITEMAP_DATA_DIR
    echo '{"items":[]}' > $SITEMAP_DATA_DIR/sitemap-data.json
    log "📦 Создан пустой файл данных для sitemap"
  fi

  # Сборка фронтенда с настройками для статической сборки
  log "🔨 Сборка фронтенда..."
  # Установка переменных среды для статической сборки
  export BUILD_MODE=static
  export NEXT_PUBLIC_USE_LOCAL_SITEMAP_DATA=true

  # Первая попытка сборки
  if ! docker-compose -f "$COMPOSE_FILE" build frontend; then
    log "⚠️ Произошла ошибка при первой попытке сборки фронтенда"
    log "🔄 Повторная сборка без линтинга..."
    docker-compose -f "$COMPOSE_FILE" build frontend --build-arg NEXT_PUBLIC_BUILD_MODE=static --build-arg NEXT_PUBLIC_USE_LOCAL_SITEMAP_DATA=true
    check_error "Не удалось собрать фронтенд"
  fi

  # Останавливаем временный прокси
  log "🛑 Остановка временного прокси"
  docker stop $PROXY_ID
  docker rm $PROXY_ID

  # Запускаем фронтенд
  log "🚀 Запускаем собранный фронтенд..."
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

log "🛠️ Проверяем наличие миграций Alembic..."
if [ -z "$(docker-compose -f "$COMPOSE_FILE" exec -T backend bash -c 'ls /app/versions 2>/dev/null')" ]; then
  log "🛠️ Миграций нет — создаем начальные миграции"
  docker-compose -f "$COMPOSE_FILE" exec -T backend alembic revision --autogenerate -m "Initial migration"
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
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 -m 10 http://$DOMAIN/ || echo "failed")
  if [[ "$HTTP_STATUS" == "301" || "$HTTP_STATUS" == "302" ]]; then
    success "✅ HTTP редирект работает корректно ($HTTP_STATUS)"
  else
    log "⚠️ HTTP редирект не работает (статус: $HTTP_STATUS)"
    # Не завершаем скрипт с ошибкой - просто продолжаем
  fi

  # Проверка HTTPS (может не сработать, если DNS не настроен на локальной машине)
  HTTPS_STATUS=$(curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout 5 -m 10 https://$DOMAIN/ || echo "failed")
  if [[ "$HTTPS_STATUS" == "200" ]]; then
    success "✅ HTTPS доступ работает корректно"
  else
    log "⚠️ HTTPS доступ не работает. Проверьте настройку DNS для домена $DOMAIN"
    log "📋 Это нормально, если вы запускаете на сервере, где DNS для $DOMAIN ещё не настроен"
    # Не завершаем скрипт с ошибкой
  fi
else
  log "⚠️ curl не установлен, пропускаем проверку доступности"
fi

  # Запуск пост-деплойной регенерации SEO
  log "🔍 Запуск пост-деплойной регенерации SEO..."
  if [ -f "$ROOT_DIR/scripts/regenerate-seo.sh" ]; then
    # Даем системе время на полную инициализацию (30 секунд)
    sleep 30
    bash "$ROOT_DIR/scripts/regenerate-seo.sh"
  else
    log "⚠️ Скрипт regenerate-seo.sh не найден"
    # Создаем базовый скрипт regenerate-seo.sh если его нет
    cat > "$ROOT_DIR/scripts/regenerate-seo.sh" << 'EOF'
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

# Загружаем настройки окружения
if [ -f "docker/.env" ]; then
  source docker/.env
fi

# Проверяем URL сайта
SITE_URL=${NEXT_PUBLIC_BASE_URL:-"https://kvartiry26.ru"}
API_URL=${NEXT_PUBLIC_API_URL:-"https://kvartiry26.ru/api"}

log "🚀 Начинаем регенерацию SEO-контента для $SITE_URL"

# Проверяем доступность сайта
if ! curl -s -f "$SITE_URL" > /dev/null; then
  error "❌ Сайт недоступен по адресу $SITE_URL"
  exit 1
fi

# Список основных страниц для обновления
PAGES=(
  "/"
  "/catalog"
  "/sitemap.xml"
)

# Получаем список ID квартир для обновления их страниц
log "🔍 Получение списка ID квартир..."
APARTMENT_IDS=$(curl -s "${API_URL}/api/v1/apartments?page_size=20" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' 2>/dev/null || echo "")

if [ -z "$APARTMENT_IDS" ]; then
  log "⚠️ Не удалось получить ID квартир, обновляем только основные страницы"
else
  success "✅ Получены ID квартир"
  for id in $APARTMENT_IDS; do
    PAGES+=("/apartment/$id")
  done
fi

# Обновляем каждую страницу
for page in "${PAGES[@]}"; do
  log "🔄 Обновление страницы: $page"
  response=$(curl -s -o /dev/null -w "%{http_code}" "${SITE_URL}${page}")
  if [ "$response" == "200" ]; then
    success "✅ Страница $page успешно обновлена"
  else
    log "⚠️ Страница $page вернула код $response"
  fi
  # Небольшая пауза, чтобы не перегружать сервер
  sleep 1
done

# Проверяем sitemap
log "🔍 Проверка sitemap.xml..."
sitemap_content=$(curl -s "${SITE_URL}/sitemap.xml")
apartment_count=$(echo "$sitemap_content" | grep -c "/apartment/")

if [ $apartment_count -gt 0 ]; then
  success "✅ sitemap.xml содержит $apartment_count страниц квартир"
else
  log "⚠️ В sitemap.xml не найдены страницы квартир"
fi

# Обновляем данные для sitemap
log "🔄 Обновление данных для sitemap..."
mkdir -p apps/frontend/public
curl -s "${API_URL}/api/v1/apartments?page_size=40" > apps/frontend/public/sitemap-data.json
success "✅ Данные для sitemap обновлены"

success "✅ Регенерация SEO-контента завершена"
EOF
    chmod +x "$ROOT_DIR/scripts/regenerate-seo.sh"
    log "✅ Создан скрипт regenerate-seo.sh"
    bash "$ROOT_DIR/scripts/regenerate-seo.sh"
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