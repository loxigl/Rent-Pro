# Базовый образ
FROM node:20-alpine AS base

# Установка зависимостей
FROM base AS deps
WORKDIR /app

# Копирование package.json и package-lock.json
COPY package.json package-lock.json* ./

# Установка зависимостей
RUN npm ci

# Сборка приложения
FROM base AS builder
WORKDIR /app

# Копирование зависимостей
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Установка переменных окружения для сборки
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

ARG NEXT_PUBLIC_BASE_URL
ENV NEXT_PUBLIC_BASE_URL=${NEXT_PUBLIC_BASE_URL}

ARG NEXT_PUBLIC_MINIO_HOST
ENV NEXT_PUBLIC_MINIO_HOST=${NEXT_PUBLIC_MINIO_HOST}

# Сборка приложения
RUN npm run build

# Запуск приложения
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

# Создаем не-root пользователя
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Копирование необходимых файлов
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Меняем пользователя
USER nextjs

# Установка переменных окружения для запуска
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Открытие порта
EXPOSE 3000

# Запуск приложения
CMD ["node", "server.js"]