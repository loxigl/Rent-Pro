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

# Создаем виртуальное окружение для Python
if [ ! -d "venv" ]; then
  echo -e "${YELLOW}🐍 Создаем виртуальное окружение Python...${NC}"
  python -m venv venv
  echo -e "${GREEN}✅ Виртуальное окружение создано${NC}"
else
  echo -e "${YELLOW}🐍 Виртуальное окружение уже существует${NC}"
fi

# Активируем виртуальное окружение
if [ -d "venv" ]; then
  echo -e "${YELLOW}🔄 Активируем виртуальное окружение...${NC}"
  source venv/bin/activate

  # Устанавливаем зависимости
  echo -e "${YELLOW}📦 Устанавливаем зависимости бэкенда...${NC}"
  pip install -r requirements.txt
  echo -e "${GREEN}✅ Зависимости бэкенда установлены${NC}"
fi

# 2. Настройка фронтенда
echo -e "\n${YELLOW}🔧 Настройка фронтенда...${NC}"
cd $ROOT_DIR/apps/frontend

# Копирование примера .env файла, если его нет
if [ ! -f .env ]; then
  echo -e "${YELLOW}📄 Создаем .env файл для фронтенда...${NC}"
  cp .env.sample .env
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

# Запускаем миграции в контейнере
echo -e "\n${YELLOW}🗃️ Запускаем миграции базы данных...${NC}"
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head
echo -e "${GREEN}✅ Миграции выполнены${NC}"

# Заполняем БД тестовыми данными
echo -e "\n${YELLOW}🧪 Заполняем БД тестовыми данными...${NC}"
docker-compose -f docker-compose.dev.yml exec backend python -m scripts.seed_data
echo -e "${GREEN}✅ БД заполнена тестовыми данными${NC}"

echo -e "\n${YELLOW}=================================================${NC}"
echo -e "${GREEN}✅ Инициализация проекта успешно завершена!${NC}"
echo -e "${YELLOW}=================================================${NC}"
echo -e "${YELLOW}📋 Инструкция по запуску:${NC}"
echo -e "${YELLOW}- Бэкенд доступен по адресу: http://localhost:8000${NC}"
echo -e "${YELLOW}- Фронтенд необходимо запустить командой: cd ../apps/frontend && npm run dev${NC}"
echo -e "${YELLOW}- API документация: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}- Админка MinIO: http://localhost:9001${NC}"
echo -e "${YELLOW}=================================================${NC}"