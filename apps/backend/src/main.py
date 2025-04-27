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
from src.db.database import engine, Base
from src.models.auth import initialize_permissions
from src.db.database import SessionLocal

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
    version="0.2.0",
)

# Настройка CORS
origins = [
    "http://localhost:3000",  # Frontend dev
    "http://localhost:8000",  # Backend dev
    "https://kvartiry26.ru",  # Frontend prod
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


# Подключение публичных API-роутеров
from src.api.apartments import router as apartments_router

app.include_router(apartments_router, prefix=settings.API_PREFIX)

# Подключение API-роутеров для админ-панели
from src.api.admin import admin_router

app.include_router(admin_router)


# Корневой эндпоинт
@app.get("/")
async def root():
    return {"message": "AvitoRentPro API v0.2.0"}


# Инициализация при запуске приложения
@app.on_event("startup")
async def startup_event():
    # Создаем таблицы в базе данных (если их еще нет)
    Base.metadata.create_all(bind=engine)

    # Инициализируем разрешения для ролей
    db = SessionLocal()
    try:
        initialize_permissions(db)
        logger.info("Permissions initialized")
    except Exception as e:
        logger.error(f"Error initializing permissions: {e}")
    finally:
        db.close()


# Точка входа для запуска через uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
