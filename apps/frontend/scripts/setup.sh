#!/bin/bash
set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=================================================${NC}"
echo -e "${YELLOW}🚀 Инициализация проекта AvitoRentPro 🚀${NC}"
echo -e "${YELLOW}=================================================${NC}"

# Получаем корневую директорию проекта
ROOT_DIR=$(pwd)

# Создаем необходимые директории
mkdir -p docker/certbot/conf
mkdir -p docker/certbot/www

# 1. Настройка бэкенда
echo -e "\n${YELLOW}🔧 Настройка бэкенда...${NC}"
cd $ROOT_DIR/apps/backend

# Копирование примера .env файла, если его нет
if [ ! -f .env ]; then
  echo -e "${YELLOW}📄 Создаем .env файл для бэкенда...${NC}"
  cp .env.sample .env
  echo -e "${GREEN}✅ Файл .env создан${NC}"
else
  echo -e "${YELLOW}📄 Файл .env уже существует${NC}"
fi

# Удаляем существующее виртуальное окружение, если оно повреждено
if [ -d "venv" ]; then
  echo -e "${YELLOW}🔄 Удаляем существующее виртуальное окружение...${NC}"
  rm -rf venv
  echo -e "${GREEN}✅ Старое виртуальное окружение удалено${NC}"
fi

# Создаем новое виртуальное окружение для Python
echo -e "${YELLOW}🐍 Создаем новое виртуальное окружение Python...${NC}"
python3 -m venv venv --system-site-packages
echo -e "${GREEN}✅ Виртуальное окружение создано${NC}"

# Устанавливаем зависимости
echo -e "${YELLOW}📦 Устанавливаем зависимости бэкенда...${NC}"
# Проверяем наличие файла activate
if [ ! -f "venv/bin/activate" ]; then
  echo -e "${RED}❌ Файл activate не найден в виртуальном окружении!${NC}"
  echo -e "${YELLOW}🔍 Проверяем структуру виртуального окружения...${NC}"
  ls -la venv/bin/
  echo -e "${YELLOW}🔄 Пробуем альтернативный способ установки зависимостей...${NC}"
  venv/bin/python -m pip install --upgrade pip
  venv/bin/python -m pip install -r requirements.txt
else
  echo -e "${GREEN}✅ Файл activate найден${NC}"
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  deactivate
fi
echo -e "${GREEN}✅ Зависимости бэкенда установлены${NC}"

# 2. Настройка фронтенда
echo -e "\n${YELLOW}🔧 Настройка фронтенда...${NC}"
cd $ROOT_DIR/apps/frontend

# Копирование примера .env файла, если его нет
if [ ! -f .env ]; then
  echo -e "${YELLOW}📄 Создаем .env файл для фронтенда...${NC}"
  cp .env.sample .env
  # Обновляем API URL для корректной работы с бэкендом
  sed -i -e 's|NEXT_PUBLIC_API_URL=http://localhost:8000|NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1|g' .env || true
  echo -e "${GREEN}✅ Файл .env создан${NC}"
else
  echo -e "${YELLOW}📄 Файл .env уже существует${NC}"
fi

# Устанавливаем зависимости через npm
echo -e "${YELLOW}📦 Устанавливаем зависимости фронтенда...${NC}"
npm install
echo -e "${GREEN}✅ Зависимости фронтенда установлены${NC}"

# 3. Запуск docker-compose для разработки
echo -e "\n${YELLOW}🐳 Запуск docker-compose для разработки...${NC}"
cd $ROOT_DIR/docker

# Копирование примера .env файла, если его нет
if [ ! -f .env ]; then
  echo -e "${YELLOW}📄 Создаем .env файл для docker...${NC}"
  cp .env.sample .env
  echo -e "${GREEN}✅ Файл .env создан${NC}"
else
  echo -e "${YELLOW}📄 Файл .env уже существует${NC}"
fi

# Запускаем docker-compose
echo -e "${YELLOW}🔄 Запускаем контейнеры для разработки...${NC}"
docker-compose -f docker-compose.dev.yml up -d
echo -e "${GREEN}✅ Контейнеры запущены${NC}"

# Даем контейнерам время на полный запуск
echo -e "${YELLOW}⏳ Ожидание полного запуска контейнеров...${NC}"
sleep 10

# Запускаем миграции в контейнере (с повторными попытками)
echo -e "\n${YELLOW}🗃️ Запускаем миграции базы данных...${NC}"
MAX_RETRIES=5
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head; then
    echo -e "${GREEN}✅ Миграции выполнены${NC}"
    break
  else
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo -e "${YELLOW}⚠️ Попытка $RETRY_COUNT из $MAX_RETRIES. Подождите, пока сервисы полностью запустятся...${NC}"
    sleep 5
  fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo -e "${RED}❌ Не удалось выполнить миграции после $MAX_RETRIES попыток${NC}"
fi

# Заполняем БД тестовыми данными
echo -e "\n${YELLOW}🧪 Заполняем БД тестовыми данными...${NC}"
docker-compose -f docker-compose.dev.yml exec backend python -m scripts.seed_data || echo -e "${YELLOW}⚠️ Не удалось заполнить БД тестовыми данными, возможно они уже существуют${NC}"
echo -e "${GREEN}✅ Процесс инициализации БД завершен${NC}"

echo -e "\n${YELLOW}=================================================${NC}"
echo -e "${GREEN}✅ Инициализация проекта успешно завершена!${NC}"
echo -e "${YELLOW}=================================================${NC}"
echo -e "${YELLOW}📋 Инструкция по запуску:${NC}"
echo -e "${YELLOW}- Бэкенд доступен по адресу: http://localhost:8000${NC}"
echo -e "${YELLOW}- Запустите фронтенд командой: cd ${ROOT_DIR}/apps/frontend && npm run dev${NC}"
echo -e "${YELLOW}- API документация: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}- Админка MinIO: http://localhost:9001${NC}"
echo -e "${YELLOW}=================================================${NC}"