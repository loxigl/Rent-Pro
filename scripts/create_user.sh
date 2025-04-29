#!/bin/bash
set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=================================================${NC}"
echo -e "${YELLOW}🚀 Создание пользователя для AvitoRentPro 🚀${NC}"
echo -e "${YELLOW}=================================================${NC}"

# Получаем корневую директорию проекта
ROOT_DIR=$(pwd)

# Проверяем, запущен ли Docker
if docker ps | grep -q "avitorentpro.*backend"; then
    echo -e "${YELLOW}📦 Запуск в Docker контейнере...${NC}"
    # Определяем имя контейнера
    CONTAINER=$(docker ps --format '{{.Names}}' | grep backend | head -n 1)

    if [ -n "$CONTAINER" ]; then
        # Передаем все аргументы в скрипт внутри контейнера
        docker exec -it $CONTAINER python -m scripts.create_user "$@"
    else
        echo -e "${RED}❌ Контейнер backend не найден${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}🖥️ Запуск локально...${NC}"

    # Проверяем наличие виртуального окружения
    if [ -d "apps/backend/venv" ]; then
        source apps/backend/venv/bin/activate
    fi

    # Запускаем скрипт
    cd apps/backend
    python -m scripts.create_user "$@"
fi

echo -e "${YELLOW}=================================================${NC}"