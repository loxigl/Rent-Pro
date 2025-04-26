from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import uvicorn
from os import path
import sys

# Добавляем путь к директории src в PYTHONPATH
sys.path.append(path.dirname(path.abspath(__file__)))

from src.config.settings import settings

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)
logger = logging.getLogger("api")

# Создание FastAPI приложения
app = FastAPI(
    title="AvitoRentPro API",
    description="API для сервиса аренды квартир AvitoRentPro",
    version="0.1.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для продакшена заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f'{{"method": "{request.method}", "path": "{request.url.path}", '
        f'"status_code": {response.status_code}, "processing_time_ms": {process_time * 1000:.2f}}}'
    )

    return response


# Обработчик для 404 ошибки
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Запрашиваемый ресурс не найден"}
    )


# Подключение роутеров из других модулей
from src.api.apartments import router as apartments_router

# Регистрация роутеров
app.include_router(apartments_router, prefix=settings.API_PREFIX)


# Корневой эндпоинт
@app.get("/")
async def root():
    return {"message": "AvitoRentPro API v0.1.0"}


# Точка входа для запуска через uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)