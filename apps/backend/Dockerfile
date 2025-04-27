FROM python:3.12-slim as builder

# Установка необходимых пакетов и создание виртуального окружения
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    python -m venv /opt/venv
    
# Установка переменной окружения для использования виртуального окружения
ENV PATH="/opt/venv/bin:$PATH"

# Копируем и устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Основной образ
FROM python:3.12-slim

# Установка необходимых runtime-зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копирование виртуального окружения из промежуточного образа
COPY --from=builder /opt/venv /opt/venv

# Установка переменной окружения для использования виртуального окружения
ENV PATH="/opt/venv/bin:$PATH"

# Копируем код приложения
WORKDIR /app
COPY . .

# Установка CMD для запуска приложения
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]