#!/bin/bash
set -e

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=============================================${NC}"
echo -e "${YELLOW}🧪 Запуск тестов для проекта AvitoRentPro 🧪${NC}"
echo -e "${YELLOW}=============================================${NC}"

# Функция для отображения результата
function show_result {
  if [ $1 -eq 0 ]; then
    echo -e "${GREEN}✅ $2 успешно пройдены${NC}"
  else
    echo -e "${RED}❌ $2 завершились с ошибками${NC}"
    FAILED=1
  fi
}

# Флаг для отслеживания ошибок
FAILED=0

# Получаем корневую директорию проекта
ROOT_DIR=$(pwd)

# 1. Запуск бэкенд тестов
echo -e "\n${YELLOW}🔍 Запуск тестов бэкенда...${NC}"
cd $ROOT_DIR/apps/backend

echo -e "\n${YELLOW}🔹 Запуск юнит-тестов...${NC}"
python -m pytest -xvs tests/test_apartments.py || BACKEND_UNIT_FAILED=$?
show_result $BACKEND_UNIT_FAILED "Юнит-тесты бэкенда"

echo -e "\n${YELLOW}🔹 Проверка покрытия тестами...${NC}"
python -m pytest --cov=src --cov-report=term-missing tests/ || BACKEND_COV_FAILED=$?
show_result $BACKEND_COV_FAILED "Проверка покрытия тестами"

# 2. Запуск фронтенд тестов
echo -e "\n${YELLOW}🔍 Запуск тестов фронтенда...${NC}"
cd $ROOT_DIR/apps/frontend

echo -e "\n${YELLOW}🔹 Запуск ESLint...${NC}"
npm run lint || FRONTEND_LINT_FAILED=$?
show_result $FRONTEND_LINT_FAILED "ESLint проверка"

echo -e "\n${YELLOW}🔹 Запуск E2E тестов Playwright...${NC}"
# Убедитесь, что приложение запущено для тестирования
npm run build || FRONTEND_BUILD_FAILED=$?
show_result $FRONTEND_BUILD_FAILED "Сборка фронтенда"

if [ -z "$FRONTEND_BUILD_FAILED" ] || [ $FRONTEND_BUILD_FAILED -eq 0 ]; then
  npx playwright test || PLAYWRIGHT_FAILED=$?
  show_result $PLAYWRIGHT_FAILED "E2E тесты Playwright"
else
  echo -e "${RED}⚠️ Пропуск E2E тестов из-за ошибки сборки${NC}"
fi

# 3. Запуск Lighthouse тестов производительности
echo -e "\n${YELLOW}🔍 Запуск Lighthouse тестов производительности...${NC}"
cd $ROOT_DIR/apps/frontend
if [ -z "$FRONTEND_BUILD_FAILED" ] || [ $FRONTEND_BUILD_FAILED -eq 0 ]; then
  # Запускаем отдельный процесс для сервера на порту 3000
  npm run start &
  SERVER_PID=$!

  # Ждем, пока сервер запустится
  echo "Ожидаем запуска сервера..."
  sleep 5

  # Запускаем Lighthouse тесты
  node scripts/lighthouse.js || LIGHTHOUSE_FAILED=$?
  show_result $LIGHTHOUSE_FAILED "Lighthouse тесты"

  # Останавливаем сервер
  kill $SERVER_PID
else
  echo -e "${RED}⚠️ Пропуск Lighthouse тестов из-за ошибки сборки${NC}"
fi

# 4. Запуск нагрузочных тестов Locust (если установлен)
echo -e "\n${YELLOW}🔍 Запуск нагрузочных тестов Locust...${NC}"
cd $ROOT_DIR

if command -v locust &> /dev/null; then
  # Проверяем, работают ли сервисы
  if curl -s http://localhost:8000/api/v1/apartments > /dev/null; then
    # Запускаем Locust в headless режиме на 30 секунд с 10 пользователями
    locust -f tests/locustfile.py --host=http://localhost:8000 --headless -u 10 -r 1 -t 30s || LOCUST_FAILED=$?
    show_result $LOCUST_FAILED "Нагрузочные тесты Locust"
  else
    echo -e "${RED}⚠️ Пропуск нагрузочных тестов, так как API не доступен${NC}"
  fi
else
  echo -e "${YELLOW}⚠️ Locust не установлен, пропуск нагрузочных тестов${NC}"
fi

# Общий результат
echo -e "\n${YELLOW}=============================================${NC}"
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✅ Все тесты успешно пройдены!${NC}"
  exit 0
else
  echo -e "${RED}❌ Некоторые тесты завершились с ошибками${NC}"
  exit 1
fi