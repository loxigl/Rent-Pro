from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from src.db.database import get_db
from src.models.apartment import Apartment, ApartmentPhoto
from src.schemas.apartment import ApartmentInList, ApartmentDetail, PaginatedApartments
from src.config.settings import settings
from src.services.minio_service import MinioService
from src.services.apartment_service import ApartmentService
from src.services.image_service import ImageSize, ImageFormat
from src.services.cache_service import CacheService
from src.celery_worker import process_image

router = APIRouter(tags=["apartments"])

# Инициализация сервисов
minio_service = MinioService()
cache_service = CacheService()


# Функция для инвалидации кеша квартиры
def invalidate_apartment_cache(apartment_id: int):
    """Фоновая задача для инвалидации кеша квартиры."""
    cache_service.invalidate_apartment_cache(apartment_id)
    cache_service.invalidate_apartments_cache()


# Эндпоинт для получения списка квартир
@router.get("/apartments", response_model=PaginatedApartments)
async def get_apartments(
        page: int = Query(1, ge=1),
        page_size: int = Query(12, ge=6, le=40),
        sort: str = Query("created_at", regex="^(created_at|price_rub)$"),
        order: str = Query("desc", regex="^(asc|desc)$"),
        db: Session = Depends(get_db)
):
    """
    Получение списка квартир с пагинацией и сортировкой.

    Args:
        page: Номер страницы (от 1)
        page_size: Количество элементов на странице (от 6 до 40)
        sort: Поле для сортировки (created_at или price_rub)
        order: Порядок сортировки (asc или desc)
        db: Сессия БД

    Returns:
        PaginatedApartments: Пагинированный список квартир
    """
    # Формируем ключ кеша
    cache_key = cache_service.get_apartments_cache_key(page, page_size, sort, order)

    # Пытаемся получить результат из кеша
    cached_result = cache_service.get(cache_key)
    if cached_result:
        return cached_result

    # Если в кеше нет, получаем данные из БД
    apartments, total = ApartmentService.get_apartments(db, page, page_size, sort, order)

    # Подготавливаем данные для ответа
    apartment_list = []
    for apartment in apartments:
        # Получаем обложку с предпочтением webp формата для производительности
        apartment_item = ApartmentService.create_apartment_list_item(
            db, apartment, preferred_variant="small_webp"
        )
        apartment_list.append(apartment_item)

    # Формируем ответ
    result = PaginatedApartments(
        page=page,
        page_size=page_size,
        total=total,
        items=apartment_list
    )

    # Сохраняем результат в кеш
    cache_service.set(cache_key, result, expire=300)  # Кешируем на 5 минут

    return result


# Эндпоинт для получения детальной информации о квартире
@router.get("/apartments/{apartment_id}", response_model=ApartmentDetail)
async def get_apartment(
        apartment_id: int,
        db: Session = Depends(get_db)
):
    """
    Получение детальной информации о квартире по ID.

    Args:
        apartment_id: ID квартиры
        db: Сессия БД

    Returns:
        ApartmentDetail: Детальная информация о квартире
    """
    # Формируем ключ кеша
    cache_key = cache_service.get_apartment_cache_key(apartment_id)

    # Пытаемся получить результат из кеша
    cached_result = cache_service.get(cache_key)
    if cached_result:
        return cached_result

    # Получаем квартиру по ID
    apartment = ApartmentService.get_apartment_by_id(db, apartment_id)

    if not apartment:
        raise HTTPException(status_code=404, detail="Квартира не найдена")

    # Получаем фотографии с вариантами
    photos_with_variants = ApartmentService.get_apartment_photos_with_variants(db, apartment_id)

    # Выбираем предпочтительные URL для детальной страницы (medium_webp или любые доступные)
    photo_urls = []
    for photo in photos_with_variants:
        variants = photo.get("variants", {})
        url = (
            variants.get("medium_webp") or
            variants.get("medium_jpeg") or
            variants.get("original") or
            next(iter(variants.values())) if variants else None
        )
        if url:
            photo_urls.append(url)

    # Формируем ответ
    result = ApartmentDetail(
        id=apartment.id,
        title=apartment.title,
        price_rub=apartment.price_rub,
        rooms=apartment.rooms,
        floor=apartment.floor,
        area_m2=apartment.area_m2,
        address=apartment.address,
        description=apartment.description,
        active=apartment.active,
        photos=photo_urls,
        created_at=apartment.created_at
    )

    # Сохраняем результат в кеш
    cache_service.set(cache_key, result, expire=300)  # Кешируем на 5 минут

    return result


# Эндпоинт для получения вариантов фотографий квартиры
@router.get("/apartments/{apartment_id}/photos", response_model=List[Dict])
async def get_apartment_photos(
        apartment_id: int,
        db: Session = Depends(get_db)
):
    """
    Получение всех фотографий квартиры с вариантами разных размеров.

    Args:
        apartment_id: ID квартиры
        db: Сессия БД

    Returns:
        List[Dict]: Список фотографий с вариантами
    """
    # Проверяем существование квартиры
    apartment = ApartmentService.get_apartment_by_id(db, apartment_id)

    if not apartment:
        raise HTTPException(status_code=404, detail="Квартира не найдена")

    # Получаем фотографии с вариантами
    photos = ApartmentService.get_apartment_photos_with_variants(db, apartment_id)

    return photos


# Временный эндпоинт для загрузки фотографий (будет заменен в v1)
@router.post("/admin/upload", status_code=201)
async def upload_photo(
        background_tasks: BackgroundTasks,
        apartment_id: int = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """
    Временный эндпоинт для загрузки фотографий.

    Args:
        background_tasks: Фоновые задачи FastAPI
        apartment_id: ID квартиры
        file: Загружаемый файл
        db: Сессия БД

    Returns:
        dict: Информация о загруженном файле
    """
    # Проверяем существование квартиры
    apartment = ApartmentService.get_apartment_by_id(db, apartment_id)
    if not apartment:
        raise HTTPException(status_code=404, detail="Квартира не найдена")

    # Проверяем формат файла
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Поддерживаются только JPEG и PNG изображения"
        )

    try:
        # Читаем содержимое файла
        file_content = await file.read()

        # Проверяем размер файла (не более 10 МБ)
        if len(file_content) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Размер файла превышает {settings.MAX_IMAGE_SIZE_MB} МБ"
            )

        # Запускаем задачу Celery для обработки изображения
        cover_url = process_image.delay(file_content, apartment_id).get()

        # Добавляем фотографию к квартире
        new_photo = ApartmentService.add_apartment_photo(
            db,
            apartment_id,
            cover_url,
            metadata={
                "original_filename": file.filename,
                "content_type": file.content_type,
                "upload_timestamp": datetime.now().isoformat()
            }
        )

        # Инвалидируем кеш для этой квартиры в фоновом режиме
        background_tasks.add_task(invalidate_apartment_cache, apartment_id)

        # Получаем информацию о загруженном изображении
        photo_info = ApartmentService.get_apartment_photos_with_variants(db, apartment_id)
        uploaded_photo = next((p for p in photo_info if p["id"] == new_photo.id), None)

        return {
            "id": new_photo.id,
            "apartment_id": new_photo.apartment_id,
            "sort_order": new_photo.sort_order,
            "url": cover_url,
            "variants": uploaded_photo["variants"] if uploaded_photo else {}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {str(e)}")


# Эндпоинт для изменения порядка фотографий
@router.put("/admin/photos/{photo_id}/order", status_code=200)
async def update_photo_order(
        photo_id: int,
        sort_order: int = Form(...),
        background_tasks: BackgroundTasks = None,
        db: Session = Depends(get_db)
):
    """
    Изменение порядка отображения фотографии.

    Args:
        photo_id: ID фотографии
        sort_order: Новый порядок сортировки
        background_tasks: Фоновые задачи FastAPI
        db: Сессия БД

    Returns:
        dict: Информация об обновленной фотографии
    """
    try:
        # Обновляем порядок сортировки
        updated_photo = ApartmentService.update_photo_sort_order(db, photo_id, sort_order)

        if not updated_photo:
            raise HTTPException(status_code=404, detail="Фотография не найдена")

        # Инвалидируем кеш для квартиры в фоновом режиме
        if background_tasks:
            background_tasks.add_task(invalidate_apartment_cache, updated_photo.apartment_id)

        return {
            "id": updated_photo.id,
            "apartment_id": updated_photo.apartment_id,
            "sort_order": updated_photo.sort_order,
            "url": updated_photo.url
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Ошибка обновления порядка фотографии: {str(e)}")


# Эндпоинт для удаления фотографии
@router.delete("/admin/photos/{photo_id}", status_code=204)
async def delete_photo(
        photo_id: int,
        background_tasks: BackgroundTasks = None,
        db: Session = Depends(get_db)
):
    """
    Удаление фотографии.

    Args:
        photo_id: ID фотографии
        background_tasks: Фоновые задачи FastAPI
        db: Сессия БД
    """
    try:
        # Получаем фотографию для определения apartment_id перед удалением
        photo = db.query(ApartmentPhoto).filter(ApartmentPhoto.id == photo_id).first()

        if not photo:
            raise HTTPException(status_code=404, detail="Фотография не найдена")

        apartment_id = photo.apartment_id

        # Удаляем фотографию
        success = ApartmentService.delete_photo(db, photo_id)

        if not success:
            raise HTTPException(status_code=404, detail="Ошибка удаления фотографии")

        # Инвалидируем кеш для квартиры в фоновом режиме
        if background_tasks:
            background_tasks.add_task(invalidate_apartment_cache, apartment_id)

        return None  # 204 No Content

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Ошибка удаления фотографии: {str(e)}")