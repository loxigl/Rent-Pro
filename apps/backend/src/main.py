from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.gzip import GZipMiddleware
import logging
import time
import uvicorn
from os import path
import sys
import os
from fastapi.staticfiles import StaticFiles

# Добавляем путь к директории src в PYTHONPATH
sys.path.append(path.dirname(path.abspath(__file__)))

from src.config.settings import settings
from src.db.database import engine, Base
from src.models.auth import initialize_permissions
from src.db.database import SessionLocal
from src.api import (
    auth_router, apartment_router, image_router,
    bookings_router, admin_router, settings_router
)

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)
logger = logging.getLogger("api")

# Определение префикса для API

ApiPath="/api"
# Создание FastAPI приложения
app = FastAPI(
    title="AvitoRentPro API",
    description="API для сервиса аренды квартир",
    version="1.0.0",
    docs_url=f"/docs",
    redoc_url=f"/redoc",
    openapi_url=f"/openapi.json",
    root_path="/api"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost",
                   "http://localhost:3000, https://localhost:3000, https://kvartiry26.ru, https://admin.kvartiry26.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавление Gzip сжатия
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Обработка ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


# Регистрация маршрутов с префиксом /api
app.include_router(auth_router)
app.include_router(apartment_router)
app.include_router(image_router)
app.include_router(bookings_router)
app.include_router(settings_router)
app.include_router(admin_router)

# Настройка статических файлов
static_dir = os.path.join(os.getcwd(), settings.STATIC_DIR)
os.makedirs(static_dir, exist_ok=True)

upload_dir = os.path.join(static_dir, settings.UPLOAD_DIR)
os.makedirs(upload_dir, exist_ok=True)

app.mount(f"/static", StaticFiles(directory=static_dir), name="static")


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


@app.get(f"/health")
async def health_check():
    return {"status": "ok"}


# Точка входа для запуска через uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
