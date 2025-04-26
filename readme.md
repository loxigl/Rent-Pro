# AvitoRentPro - MVP-0

Система каталога квартир для аренды в г. Невинномысск. MVP-0 включает публичный каталог карточек с возможностью просмотра детальной информации о квартирах и контактными данными для связи.

## 🚀 Технологический стек

### Backend:
- Python 3.12
- FastAPI
- SQLAlchemy 2
- Pydantic v2
- PostgreSQL 16
- MinIO (S3-совместимое хранилище)
- Celery + Redis
- Docker & Docker Compose

### Frontend:
- Next.js 14 (App Router)
- React 19
- Tailwind CSS 3.5
- Swiper (для галереи изображений)
- TypeScript

## 📋 Функциональность MVP-0

1. **Каталог квартир**:
   - Пагинация и сортировка по цене/дате
   - Отображение карточек с основной информацией
   - SSG с инкрементальной регенерацией (ISR)

2. **Детальная страница квартиры**:
   - Галерея изображений с возможностью увеличения
   - Таблица характеристик квартиры
   - Markdown-описание
   - Кнопки для связи по телефону и через Telegram
   - SSR с кешированием

3. **Оптимизация для SEO и производительности**:
   - Метаданные для каждой страницы
   - Оптимизированные изображения (разные размеры, WebP формат)
   - Sitemap, robots.txt, Schema.org разметка
   - Оптимизация производительности для мобильных устройств

## 🛠️ Установка и запуск

### Быстрый старт с помощью скрипта

```bash
# Клонировать репозиторий
git clone https://github.com/yourusername/AvitoRentPro.git
cd AvitoRentPro

# Запустить скрипт инициализации
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Ручная установка

#### 1. Настройка бэкенда:

```bash
cd apps/backend

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл (на основе .env.sample)
cp .env.sample .env
```

#### 2. Настройка фронтенда:

```bash
cd apps/frontend

# Установить зависимости
npm install

# Создать .env файл (на основе .env.sample)
cp .env.sample .env
```

#### 3. Запуск Docker-контейнеров:

```bash
cd docker

# Создать .env файл (на основе .env.sample)
cp .env.sample .env

# Запустить контейнеры
docker-compose -f docker-compose.dev.yml up -d
```

#### 4. Применить миграции и заполнить тестовыми данными:

```bash
# Применить миграции
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

# Заполнить БД тестовыми данными
docker-compose -f docker-compose.dev.yml exec backend python -m scripts.seed_data
```

#### 5. Запуск фронтенда:

```bash
cd apps/frontend
npm run dev
```

## 🧪 Тестирование

### Запуск всех тестов:

```bash
chmod +x scripts/test.sh
./scripts/test.sh
```

### Отдельные тесты:

```bash
# Бэкенд тесты
cd apps/backend
pytest

# E2E тесты фронтенда
cd apps/frontend
npx playwright test

# Lighthouse тесты
node scripts/lighthouse.js

# Нагрузочное тестирование
locust -f tests/locustfile.py
```

## 📊 Производительность

Проект оптимизирован в соответствии с требованиями Performance Budget:

- LCP (Largest Contentful Paint): < 2.5s
- INP (Interaction to Next Paint): < 200ms
- JS Bundle Size (initial): ≤ 70kB gzipped
- CLS (Cumulative Layout Shift): < 0.1

## 🚀 Деплой

### Продакшен-деплой:

```bash
# Настройка переменных окружения
cd docker
cp .env.sample .env
# Отредактировать .env файл

# Запуск стека
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 Лицензия

Проект разрабатывается для внутреннего использования.

## ✨ Следующие шаги

Планы развития:
- Модуль бронирования
- Интеграция с Авито API
- Telegram-бот для уведомлений
- Административная панель