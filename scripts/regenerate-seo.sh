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
sitemap_content=$(curl -s "${SITE_URL}/sitemap.xml" || true)

if [ -n "$sitemap_content" ]; then
  apartment_count=$(echo "$sitemap_content" | grep -c "/apartment/" || true)
else
  apartment_count=0
fi

if [ "$apartment_count" -gt 0 ]; then
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