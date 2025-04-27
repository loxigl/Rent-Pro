#!/bin/bash
set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=================================================${NC}"
echo -e "${YELLOW}🛠️ Инициализация MinIO для AvitoRentPro 🛠️${NC}"
echo -e "${YELLOW}=================================================${NC}"

# Загрузка переменных окружения
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Настройка переменных по умолчанию, если они не заданы
MINIO_ROOT_USER=${MINIO_ROOT_USER:-minio}
MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-minio123}
MINIO_HOST=${MINIO_HOST:-localhost}
MINIO_PORT=${MINIO_PORT:-9000}
MINIO_BUCKET=${MINIO_BUCKET:-apartments}

# Проверка наличия mc (MinIO client)
if ! command -v mc &> /dev/null; then
    echo -e "${YELLOW}⚠️ MinIO client не найден, установка...${NC}"

    # Скачиваем и устанавливаем mc для соответствующей платформы
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
        chmod +x mc
        sudo mv mc /usr/local/bin/
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        curl -O https://dl.min.io/client/mc/release/darwin-amd64/mc
        chmod +x mc
        sudo mv mc /usr/local/bin/
    else
        echo -e "${RED}❌ Неподдерживаемая платформа. Пожалуйста, установите mc вручную.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ MinIO client установлен${NC}"
fi

# Настройка подключения к MinIO
echo -e "${YELLOW}🔄 Настройка подключения к MinIO...${NC}"
mc alias set avitorentpro http://${MINIO_HOST}:${MINIO_PORT} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Проверка доступности сервера MinIO
if ! mc admin info avitorentpro > /dev/null 2>&1; then
    echo -e "${RED}❌ Не удалось подключиться к серверу MinIO. Убедитесь, что сервер запущен.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Подключение к MinIO установлено${NC}"

# Создание бакета (если он еще не существует)
echo -e "${YELLOW}🔄 Создание бакета '${MINIO_BUCKET}'...${NC}"
if ! mc ls avitorentpro/${MINIO_BUCKET} > /dev/null 2>&1; then
    mc mb avitorentpro/${MINIO_BUCKET}
    echo -e "${GREEN}✅ Бакет '${MINIO_BUCKET}' создан${NC}"
else
    echo -e "${YELLOW}⚠️ Бакет '${MINIO_BUCKET}' уже существует${NC}"
fi

# Установка публичной политики для бакета
echo -e "${YELLOW}🔄 Установка политики доступа для бакета...${NC}"

# Создание временного файла политики
POLICY_FILE=$(mktemp)
cat > ${POLICY_FILE} << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "*"
        ]
      },
      "Action": [
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::${MINIO_BUCKET}/*"
      ]
    }
  ]
}
EOF

# Применение политики
mc policy set-json ${POLICY_FILE} avitorentpro/${MINIO_BUCKET}
rm ${POLICY_FILE}

echo -e "${GREEN}✅ Политика доступа установлена${NC}"

# Проверка загрузки тестового файла
echo -e "${YELLOW}🔄 Тестирование загрузки и доступа...${NC}"

# Создание временного тестового файла
TEST_FILE=$(mktemp)
echo "AvitoRentPro MinIO test file" > ${TEST_FILE}

# Загрузка тестового файла
mc cp ${TEST_FILE} avitorentpro/${MINIO_BUCKET}/test.txt
rm ${TEST_FILE}

# Проверка доступа по публичной ссылке
TEST_URL="http://${MINIO_HOST}:${MINIO_PORT}/${MINIO_BUCKET}/test.txt"
if curl -s -f ${TEST_URL} > /dev/null; then
    echo -e "${GREEN}✅ Файл успешно загружен и доступен по ссылке: ${TEST_URL}${NC}"
else
    echo -e "${RED}❌ Не удалось получить доступ к загруженному файлу. Проверьте конфигурацию сети.${NC}"
fi

# Удаление тестового файла
mc rm avitorentpro/${MINIO_BUCKET}/test.txt

echo -e "${GREEN}✅ Тест завершен${NC}"

echo -e "\n${YELLOW}=================================================${NC}"
echo -e "${GREEN}✅ Инициализация MinIO успешно завершена!${NC}"
echo -e "${YELLOW}=================================================${NC}"
echo -e "${YELLOW}📋 Информация:${NC}"
echo -e "${YELLOW}- MinIO сервер: http://${MINIO_HOST}:${MINIO_PORT}${NC}"
echo -e "${YELLOW}- MinIO консоль: http://${MINIO_HOST}:9001${NC}"
echo -e "${YELLOW}- Логин: ${MINIO_ROOT_USER}${NC}"
echo -e "${YELLOW}- Пароль: ${MINIO_ROOT_PASSWORD}${NC}"
echo -e "${YELLOW}- Бакет: ${MINIO_BUCKET}${NC}"
echo -e "${YELLOW}=================================================${NC}"