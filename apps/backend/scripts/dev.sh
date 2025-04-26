#!/bin/bash
set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=================================================${NC}"
echo -e "${YELLOW}🚀 Запуск окружения разработки AvitoRentPro 🚀${NC}"
echo -e "${YELLOW}=================================================${NC}"

# Получаем корневую директорию проекта
ROOT_DIR=$(pwd)

# Проверяем, запущен ли docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker не запущен. Пожалуйста, запустите Docker и повторите попытку.${NC}"
    exit 1
fi

# Переходим в директорию docker
cd ${ROOT_DIR}/docker

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📄 Файл .env не найден, копируем из .env.sample...${NC}"
    cp .env.sample .env
    echo -e "${GREEN}✅ Файл .env создан${NC}"
fi

# Запускаем docker-compose
echo -e "${YELLOW}🐳 Запуск контейнеров...${NC}"
docker-compose -f docker-compose.dev.yml up -d
echo -e "${GREEN}✅ Контейнеры запущены${NC}"

# Проверяем, нужно ли применить миграции
echo -e "${YELLOW}🔄 Проверка миграций...${NC}"
MIGRATION_STATUS=$(docker-compose -f docker-compose.dev.yml exec -T backend alembic current 2>/dev/null || echo "No migration")

if [[ $MIGRATION_STATUS == *"No migration"* ]]; then
    echo -e "${YELLOW}📦 Применение миграций...${NC}"
    docker-compose -f docker-compose.dev.yml exec -T backend alembic upgrade head
    echo -e "${GREEN}✅ Миграции применены${NC}"
else
    echo -e "${GREEN}✅ Миграции уже применены${NC}"
fi

# Проверяем наличие данных в БД
echo -e "${YELLOW}🔄 Проверка данных в БД...${NC}"
APARTMENT_COUNT=$(docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d avitorentpro -c "SELECT COUNT(*) FROM apartment;" -t 2>/dev/null || echo "0")
APARTMENT_COUNT=$(echo $APARTMENT_COUNT | tr -d ' ')

if [[ $APARTMENT_COUNT == "0" || $APARTMENT_COUNT == *"does not exist"* ]]; then
    echo -e "${YELLOW}🧪 Заполнение БД тестовыми данными...${NC}"
    docker-compose -f docker-compose.dev.yml exec -T backend python -m scripts.seed_data
    echo -e "${GREEN}✅ БД заполнена тестовыми данными${NC}"
else
    echo -e "${GREEN}✅ В БД уже есть $APARTMENT_COUNT записей квартир${NC}"
fi

# Переходим в директорию frontend и запускаем dev-сервер
echo -e "${YELLOW}🔄 Запуск frontend dev-сервера...${NC}"
cd ${ROOT_DIR}/apps/frontend

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📄 Файл .env не найден, копируем из .env.sample...${NC}"
    cp .env.sample .env
    echo -e "${GREEN}✅ Файл .env создан${NC}"
fi

# Проверяем, установлены ли зависимости
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Установка зависимостей frontend...${NC}"
    npm install
    echo -e "${GREEN}✅ Зависимости установлены${NC}"
fi

# Запускаем dev-сервер
echo -e "${YELLOW}🚀 Запуск frontend dev-сервера...${NC}"
echo -e "${GREEN}✅ Окружение разработки запущено!${NC}"
echo -e "${YELLOW}📋 Доступные URL-адреса:${NC}"
echo -e "${YELLOW}- Frontend: http://localhost:3000${NC}"
echo -e "${YELLOW}- API: http://localhost:8000/api/v1${NC}"
echo -e "${YELLOW}- API документация: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}- MinIO консоль: http://localhost:9001${NC}"
echo -e "${YELLOW}=================================================${NC}"
echo -e "${YELLOW}💡 Для остановки окружения используйте Ctrl+C и затем запустите:${NC}"
echo -e "${YELLOW}   cd ${ROOT_DIR}/docker && docker-compose -f docker-compose.dev.yml down${NC}"
echo -e "${YELLOW}=================================================${NC}"

# Запускаем dev-сервер в интерактивном режиме
npm run dev