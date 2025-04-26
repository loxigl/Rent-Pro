#!/bin/bash
set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=================================================${NC}"
echo -e "${YELLOW}🚀 Запуск frontend AvitoRentPro 🚀${NC}"
echo -e "${YELLOW}=================================================${NC}"

# Получаем корневую директорию проекта
ROOT_DIR=$(pwd)

# Переходим в директорию frontend
cd ${ROOT_DIR}/apps/frontend

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📄 Файл .env не найден, копируем из .env.sample...${NC}"
    cp .env.sample .env
    # Обновляем API URL для корректной работы с бэкендом
    sed -i -e 's|NEXT_PUBLIC_API_URL=http://localhost:8000|NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1|g' .env
    echo -e "${GREEN}✅ Файл .env создан и настроен${NC}"
fi

# Проверяем, установлены ли зависимости
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Установка зависимостей frontend...${NC}"
    npm install
    echo -e "${GREEN}✅ Зависимости установлены${NC}"
fi

# Запускаем dev-сервер
echo -e "${YELLOW}🚀 Запуск frontend dev-сервера...${NC}"
npm run dev