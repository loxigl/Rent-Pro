# 🏠 AvitoRentPro — MVP-0

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/AvitoRentPro/actions)
[![License](https://img.shields.io/badge/license-Internal-blue)](#лицензия)
[![Tech Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20Next.js%20%7C%20PostgreSQL%20%7C%20Docker-blueviolet)](#-технологии)

> Каталог квартир для аренды в г. Невинномысск. Современный стек, удобный интерфейс, быстрый поиск и просмотр объектов.

---

## ✨ Возможности

- 📋 Публичный каталог квартир с фильтрами и сортировкой
- 🖼️ Галерея изображений и подробная карточка объекта
- 📱 Контакты для связи (телефон, Telegram)
- ⚡ Быстрая загрузка, SEO-оптимизация, SSR/SSG
- 🛡️ Админ-панель (в разработке)
- 🗄️ Хранение изображений в MinIO (S3)
- 📦 Docker-окружение для быстрого старта

---

## 🚀 Технологии

**Backend:**  
<img src="https://img.shields.io/badge/Python-3.12-blue?logo=python"/> <img src="https://img.shields.io/badge/FastAPI-1.0-green?logo=fastapi"/> <img src="https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql"/> <img src="https://img.shields.io/badge/MinIO-S3-red?logo=minio"/> <img src="https://img.shields.io/badge/Celery-5.3-green?logo=celery"/> <img src="https://img.shields.io/badge/Redis-7.2-red?logo=redis"/>

**Frontend:**  
<img src="https://img.shields.io/badge/Next.js-14-black?logo=next.js"/> <img src="https://img.shields.io/badge/React-19-blue?logo=react"/> <img src="https://img.shields.io/badge/TailwindCSS-3.5-blue?logo=tailwindcss"/> <img src="https://img.shields.io/badge/TypeScript-5.4-blue?logo=typescript"/>

---

## 📦 Быстрый старт

```bash
# 1. Клонируйте репозиторий
 git clone https://github.com/yourusername/AvitoRentPro.git
 cd AvitoRentPro

# 2. Запустите скрипт инициализации
 chmod +x scripts/setup.sh
 ./scripts/setup.sh
```

---

## 🛠️ Ручная установка

<details>
<summary>Показать подробную инструкцию</summary>

### 1. Бэкенд

```bash
cd apps/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
```

### 2. Фронтенд

```bash
cd apps/frontend
npm install
cp .env.sample .env
```

### 3. Docker

```bash
cd docker
cp .env.sample .env
docker-compose -f docker-compose.dev.yml up -d
```

### 4. Миграции и тестовые данные

```bash
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head
docker-compose -f docker-compose.dev.yml exec backend python -m scripts.seed_data
```

### 5. Запуск фронтенда

```bash
cd apps/frontend
npm run dev
```
</details>

---

## 🧪 Тестирование

- **Все тесты:**
  ```bash
  chmod +x scripts/test.sh
  ./scripts/test.sh
  ```
- **Бэкенд:**
  ```bash
  cd apps/backend
  pytest
  ```
- **E2E (Playwright):**
  ```bash
  cd apps/frontend
  npx playwright test
  ```
- **Lighthouse:**
  ```bash
  node scripts/lighthouse.js
  ```
- **Нагрузочное (Locust):**
  ```bash
  locust -f tests/locustfile.py
  ```

---

## 📊 Performance Budget

- LCP: < 2.5s
- INP: < 200ms
- JS Bundle: ≤ 70kB gzipped
- CLS: < 0.1

---

## 🚀 Деплой

```bash
cd docker
cp .env.sample .env
# Отредактируйте .env

docker-compose -f docker-compose.prod.yml up -d
```

---

## 🗺️ Roadmap

- [🟡] Модуль бронирования - 80%
- [ ] Интеграция с Авито API
- [ ] Telegram-бот для уведомлений
- [ ] Административная панель

---

## 🤝 Вклад

PR и предложения приветствуются! Открывайте issue или создавайте pull request.

---

## 📝 Лицензия

Проект разрабатывается для внутреннего использования.

---

## 📬 Контакты

- Telegram: [@loxigl](https://t.me/loxigl)
- Email: andrey.khalaimenko@gmail.com