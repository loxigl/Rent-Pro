#!/bin/bash
set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
function log() {
  echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

function success() {
  echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

function error() {
  echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Проверка аргументов
if [ "$#" -lt 2 ]; then
    error "Использование: $0 <домен> <email>"
    exit 1
fi

DOMAIN=$1
EMAIL=$2
ROOT_DIR=$(pwd)
CERTBOT_DIR="$ROOT_DIR/docker/certbot"

log "🔐 Начинаем настройку SSL для домена $DOMAIN с email $EMAIL"

# Проверка наличия сертификатов
if [ -f "$CERTBOT_DIR/conf/live/$DOMAIN/fullchain.pem" ]; then
    success "✅ SSL сертификаты уже существуют для домена $DOMAIN"
    exit 0
fi

# Создаем необходимые директории
log "📁 Создание директорий для certbot"
mkdir -p "$CERTBOT_DIR/conf"
mkdir -p "$CERTBOT_DIR/www"

# Проверяем, запущен ли какой-либо сервис на порту 80
if netstat -tuln | grep -q ":80 "; then
    error "⚠️ Порт 80 уже занят! Необходимо освободить порт для certbot."
    exit 1
fi

# Запускаем Nginx с временной конфигурацией для certbot
log "🚀 Запуск временного Nginx для проверки certbot"

# Создаем временную конфигурацию Nginx для certbot
NGINX_TEMP_CONF="$ROOT_DIR/docker/nginx/conf.d/temp-certbot.conf"
cat > "$NGINX_TEMP_CONF" << EOF
server {
    listen 80;
    server_name $DOMAIN;
    server_tokens off;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 "Настройка SSL для $DOMAIN...";
    }
}
EOF

log "🐳 Запуск временного Docker контейнера с Nginx"
docker run --name nginx-certbot -v "$NGINX_TEMP_CONF:/etc/nginx/conf.d/default.conf" \
  -v "$CERTBOT_DIR/www:/var/www/certbot" \
  -p 80:80 -d nginx:alpine

# Даем Nginx время на запуск
sleep 5

# Запускаем certbot для получения сертификатов
log "🛠️ Запуск certbot для получения сертификатов"
docker run --rm -v "$CERTBOT_DIR/conf:/etc/letsencrypt" \
  -v "$CERTBOT_DIR/www:/var/www/certbot" \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  --email "$EMAIL" \
  -d "$DOMAIN" \
  --agree-tos --no-eff-email

# Останавливаем временный Nginx
log "🛑 Остановка временного Nginx"
docker stop nginx-certbot
docker rm nginx-certbot

# Удаляем временный конфиг
rm "$NGINX_TEMP_CONF"

# Создаем файлы для Nginx SSL конфигурации (если их нет)
SSL_PARAMS="$CERTBOT_DIR/conf/options-ssl-nginx.conf"
SSL_DHPARAMS="$CERTBOT_DIR/conf/ssl-dhparams.pem"

if [ ! -f "$SSL_PARAMS" ]; then
    log "📝 Создание файла настроек SSL"
    cat > "$SSL_PARAMS" << EOF
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
EOF
fi

if [ ! -f "$SSL_DHPARAMS" ]; then
    log "🔑 Генерация DH параметров (это может занять несколько минут)"
    openssl dhparam -out "$SSL_DHPARAMS" 2048
fi

# Генерируем продакшн конфиг Nginx
NGINX_DEFAULT_CONF="$ROOT_DIR/docker/nginx/conf.d/default.conf"
NGINX_TEMPLATE_CONF="$ROOT_DIR/docker/nginx/default.template.conf"

log "📝 Создание production конфигурации Nginx"
cat "$NGINX_TEMPLATE_CONF" > "$NGINX_DEFAULT_CONF"

# Заменяем домен в конфиге
sed -i "s/kvartiry26.ru/$DOMAIN/g" "$NGINX_DEFAULT_CONF"

success "✅ SSL настройка успешно завершена!"
log "📋 Теперь вы можете запустить полную конфигурацию с помощью 'make prod'"