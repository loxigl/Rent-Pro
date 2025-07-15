import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile, Form, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, text
from typing import Optional, List
import logging

from src.config import settings
from src.db.database import get_db, SessionLocal
from src.models.apartment import Apartment, ApartmentPhoto
from src.models.auth import User
from src.models.event_log import EventType, EntityType
from src.schemas.admin import (
    PhotoAdminBase, PhotoAdminCreate, PhotoAdminUpdate, PhotoAdminDetail,
    PhotoAdminListItem, PhotoAdminListResponse, BulkPhotoUpdateRequest, PhotoUploadResponse
)
from src.middleware.auth import get_current_active_user
from src.middleware.acl import require_photos_read, require_photos_write
from src.services.event_log_service import log_event
from src.services.minio_service import MinioService
from src.services.image_format_service import ImageFormatService
from src.celery_worker import process_image

router = APIRouter(prefix="/photos", tags=["admin-photos"])
logger = logging.getLogger(__name__)

# Инициализация сервисов
minio_service = MinioService()


@router.get("/{apartment_id}", response_model=PhotoAdminListResponse)
async def get_apartment_photos(
        apartment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_photos_read)
):
    """
    Получение списка фотографий для конкретной квартиры.

    - **apartment_id**: ID квартиры
    """
    # Проверяем существование квартиры
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Квартира не найдена"
        )

    # Получаем фотографии квартиры
    photos = db.query(ApartmentPhoto).filter(
        ApartmentPhoto.apartment_id == apartment_id
    ).order_by(
        ApartmentPhoto.sort_order
    ).all()

    # Подготавливаем список объектов для ответа
    photo_items = []
    for photo in photos:
        # Определяем, является ли фото обложкой (первое фото считается обложкой)
        is_cover = photo.sort_order == 0

        # Получаем URL миниатюры (если есть метаданные)
        thumbnail_url = photo.url
        if photo.photo_metadata and 'variants' in photo.photo_metadata:
            variants = photo.photo_metadata.get('variants', {})
            thumbnail_url = variants.get('thumbnail_webp') or variants.get('thumbnail_jpeg') or photo.url

        # Создаем объект ответа
        photo_items.append(PhotoAdminListItem(
            id=photo.id,
            apartment_id=photo.apartment_id,
            url=photo.url,
            sort_order=photo.sort_order,
            is_cover=is_cover,
            created_at=photo.created_at,
            thumbnail_url=thumbnail_url
        ))

    # Возвращаем ответ
    return PhotoAdminListResponse(
        items=photo_items,
        total=len(photo_items)
    )


"""
Обновленный метод загрузки фотографий для решения проблемы таймаутов.
Основные изменения:
1. Увеличены таймауты для Celery
2. Добавлена проверка размера файла перед обработкой
3. Улучшена обработка ошибок
4. Добавлена асинхронная загрузка без блокировки запроса
"""


@router.post("/{apartment_id}/upload", response_model=PhotoUploadResponse)
async def upload_photo(
        request: Request,
        apartment_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(require_photos_write),
        background_tasks: BackgroundTasks = None,
):
    """
    Загрузка новой фотографии для квартиры.

    - **apartment_id**: ID квартиры
    - **file**: Файл изображения
    """
    # Проверяем существование квартиры
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Квартира не найдена"
        )

    # Проверяем формат файла с использованием нового сервиса
    if not ImageFormatService.is_supported_format(file.content_type):
        supported_formats = ImageFormatService.get_supported_formats()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неподдерживаемый формат файла: {file.content_type}. "
                   f"Поддерживаются: {', '.join(supported_formats)}"
        )

    try:
        # Читаем содержимое файла с ограничением по размеру
        # Используем ограничение из настроек или 10MB по умолчанию
        max_size = getattr(settings, 'MAX_IMAGE_SIZE_MB', 10) * 1024 * 1024
        file_content = await file.read(max_size)

        # Проверяем, что файл полностью прочитан (если нет, значит он слишком большой)
        extra_content = await file.read(1)
        if extra_content:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Размер файла превышает максимально допустимый ({max_size // (1024 * 1024)}MB)"
            )

        # Дополнительная валидация изображения
        if not ImageFormatService.validate_image_content(file_content, max_size // (1024 * 1024)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл поврежден или не является валидным изображением"
            )

        # Определяем реальный формат файла (может отличаться от content_type)
        detected_format = ImageFormatService.detect_format_from_content(file_content)
        actual_format = detected_format or file.content_type
        
        logger.info(f"Загружаем файл: {file.filename}, "
                   f"заявленный формат: {file.content_type}, "
                   f"реальный формат: {actual_format}")

        # Конвертируем в поддерживаемый формат если нужно
        original_content_type = actual_format
        if actual_format not in ["image/jpeg", "image/png", "image/webp"]:
            logger.info(f"Конвертируем {actual_format} в поддерживаемый формат")
            file_content, actual_format = ImageFormatService.convert_to_supported_format(
                file_content, actual_format
            )
            logger.info(f"Конвертация завершена: {original_content_type} -> {actual_format}")

        # Определяем порядок сортировки для нового фото
        max_sort_order = db.query(func.max(ApartmentPhoto.sort_order)).filter(
            ApartmentPhoto.apartment_id == apartment_id
        ).scalar()

        # Если нет фотографий, начинаем с 0, иначе следующий порядок
        new_sort_order = 0 if max_sort_order is None else max_sort_order + 1

        # Получаем информацию об изображении
        image_info = ImageFormatService.get_image_info(file_content)

        # Вместо блокирующего вызова Celery:
        # 1. Создаем запись в БД с временным URL
        temp_url = f"/processing/apartment_{apartment_id}_{uuid.uuid4()}.jpg"
        photo_metadata = {
            "original_filename": file.filename,
            "original_content_type": file.content_type,
            "detected_content_type": detected_format,
            "processed_content_type": actual_format,
            "was_converted": original_content_type != actual_format,
            "original_format": original_content_type,
            "image_info": image_info,
            "is_cover": new_sort_order == 0,  # Первое фото - обложка
            "processing_status": "pending"
        }

        # Добавляем фото в БД с временным URL
        new_photo = ApartmentPhoto(
            apartment_id=apartment_id,
            url=temp_url,
            sort_order=new_sort_order,
            photo_metadata=photo_metadata
        )

        db.add(new_photo)
        db.commit()
        db.refresh(new_photo)

        # 2. Запускаем обработку в Celery без ожидания результата
        logger.info("Calling process_image.delay(...)")
        task = process_image.delay(file_content, apartment_id)
        logger.info(f"Task ID: {task.id}")

        # 3. Создаем фоновую задачу для обновления записи после обработки
        async def update_photo_url():
            try:
                # Ждем завершения задачи Celery (с таймаутом)
                cover_url = task.get(timeout=300)  # 5 минут таймаут

                # Обновляем запись в БД
                db_session = SessionLocal()
                try:
                    photo = db_session.query(ApartmentPhoto).filter(ApartmentPhoto.id == new_photo.id).first()
                    if photo:
                        photo.url = cover_url
                        photo.photo_metadata.update({"processing_status": "completed"})
                        db_session.commit()
                finally:
                    db_session.close()
            except Exception as e:
                # В случае ошибки обновляем статус в БД
                logger.error(f"Error processing photo: {e}")
                db_session = SessionLocal()
                try:
                    photo = db_session.query(ApartmentPhoto).filter(ApartmentPhoto.id == new_photo.id).first()
                    if photo:
                        photo.photo_metadata.update({
                            "processing_status": "failed",
                            "error": str(e)
                        })
                        db_session.commit()
                finally:
                    db_session.close()

        # Запускаем фоновую задачу
        if background_tasks:
            background_tasks.add_task(update_photo_url)
        else:
            # Создаем новую задачу если BackgroundTasks не передан
            asyncio.create_task(update_photo_url())

        # Логируем событие
        log_event(
            db=db,
            event_type=EventType.PHOTO_UPLOADED,
            user_id=current_user.id,
            entity_type=EntityType.PHOTO,
            entity_id=str(new_photo.id),
            payload={
                "apartment_id": apartment_id,
                "filename": file.filename,
                "sort_order": new_sort_order,
                "status": "processing"
            },
            request=request
        )

        # Готовим ответ с информацией о статусе обработки
        return PhotoUploadResponse(
            id=new_photo.id,
            url=temp_url,  # Временный URL, будет обновлен после обработки
            thumbnail_url=temp_url,
            apartment_id=apartment_id,
            sort_order=new_sort_order,
            is_cover=new_sort_order == 0,
            processing_status="pending"
        )

    except HTTPException:
        # Пробрасываем HTTPException дальше
        raise
    except Exception as e:
        logger.error(f"Error uploading photo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка загрузки фотографии: {str(e)}"
        )


@router.patch("/{photo_id}", response_model=PhotoAdminDetail)
async def update_photo(
        request: Request,
        photo_id: int,
        photo_data: PhotoAdminUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_photos_write)
):
    """
    Обновление данных фотографии (сортировка, статус обложки).

    - **photo_id**: ID фотографии
    - **photo_data**: Данные для обновления
    """
    # Получаем фотографию из БД
    photo = db.query(ApartmentPhoto).filter(ApartmentPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фотография не найдена"
        )

    # Сохраняем предыдущие значения для логирования
    previous_data = {
        "sort_order": photo.sort_order,
        "is_cover": photo.photo_metadata.get("is_cover", False) if photo.photo_metadata else False
    }

    # Обновляем данные фотографии
    if photo_data.sort_order is not None:
        photo.sort_order = photo_data.sort_order

    # Обновляем метаданные фото
    if photo.photo_metadata is None:
        photo.photo_metadata = {}

    if photo_data.is_cover is not None and photo_data.is_cover:
        # Если фото устанавливается как обложка, сбрасываем флаг у других фото
        other_cover_photos = db.query(ApartmentPhoto).filter(
            ApartmentPhoto.apartment_id == photo.apartment_id,
            ApartmentPhoto.id != photo.id
        ).all()

        for other_photo in other_cover_photos:
            if other_photo.photo_metadata and other_photo.photo_metadata.get("is_cover"):
                metadata = other_photo.photo_metadata
                metadata["is_cover"] = False
                other_photo.photo_metadata = metadata

        # Устанавливаем текущее фото как обложку
        photo.photo_metadata["is_cover"] = True
    elif photo_data.is_cover is not None:
        photo.photo_metadata["is_cover"] = photo_data.is_cover

    # Сохраняем изменения в БД
    db.commit()
    db.refresh(photo)

    # Логируем событие
    log_event(
        db=db,
        event_type=EventType.PHOTO_UPDATED,
        user_id=current_user.id,
        entity_type=EntityType.PHOTO,
        entity_id=str(photo.id),
        payload={
            "previous": previous_data,
            "current": {
                "sort_order": photo.sort_order,
                "is_cover": photo.photo_metadata.get("is_cover", False) if photo.photo_metadata else False
            },
            "apartment_id": photo.apartment_id
        },
        request=request
    )

    # Формируем ответ
    return PhotoAdminDetail(
        id=photo.id,
        apartment_id=photo.apartment_id,
        url=photo.url,
        sort_order=photo.sort_order,
        is_cover=photo.photo_metadata.get("is_cover", False) if photo.photo_metadata else False,
        created_at=photo.created_at,
        metadata=photo.photo_metadata
    )


@router.post("/bulk-update", status_code=status.HTTP_200_OK)
async def bulk_update_photos(
    request: Request,
    bulk_data: BulkPhotoUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_photos_write)
):
    """
    Массовое обновление порядка фотографий одной квартиры.

    - **bulk_data.updates**: список словарей {"id": int, "sort_order": int}
    """
    # 1) Проверяем вход: уникальность ID и что payload не пустой
    photo_ids = [u["id"] for u in bulk_data.updates]
    if not photo_ids:
        raise HTTPException(status_code=400, detail="Нечего обновлять")
    if len(photo_ids) != len(set(photo_ids)):
        raise HTTPException(
            status_code=400,
            detail="Дублирование ID фотографий в запросе"
        )

    # 2) Загружаем указанные фото и проверяем, что они все из одной квартиры
    photos = db.query(ApartmentPhoto) \
               .filter(ApartmentPhoto.id.in_(photo_ids)) \
               .all()

    if len(photos) != len(photo_ids):
        raise HTTPException(
            status_code=400,
            detail="Некоторые фотографии не найдены"
        )

    auction_ids = {p.apartment_id for p in photos}
    if len(auction_ids) != 1:
        raise HTTPException(
            status_code=400,
            detail="Все фотографии должны принадлежать одной квартире"
        )
    apartment_id = auction_ids.pop()

    # 3) Подготовка мапы новых порядков и проверка уникальности sort_order в запросе
    order_map = {}
    for u in bulk_data.updates:
        sid = u["sort_order"]
        if sid in order_map.values():
            raise HTTPException(
                status_code=400,
                detail=f"Дублирование sort_order={sid} в запросе"
            )
        order_map[u["id"]] = sid

    # 4) Начинаем транзакцию и откладываем проверку уникальности до коммита
    #    (констрейнт должен быть создан как DEFERRABLE)
    db.execute(text("SET CONSTRAINTS uq_ap_photo_sort DEFERRED"))

    # 5) Подгружаем все фото этой квартиры и полностью переставляем «с нуля»
    all_photos = (
        db.query(ApartmentPhoto)
          .filter_by(apartment_id=apartment_id)
          .all()
    )

    # Сначала — по заявленному sort_order, потом «лишние»
    with_new = sorted(
        [p for p in all_photos if p.id in order_map],
        key=lambda p: order_map[p.id]
    )
    without = sorted(
        [p for p in all_photos if p.id not in order_map],
        key=lambda p: p.sort_order
    )
    reordered = with_new + without

    # Нумеруем подряд 0..N-1
    for idx, photo in enumerate(reordered):
        photo.sort_order = idx

    # 6) Коммитит всё одной пачкой, проверка UNIQUE произойдёт только здесь
    db.commit()

    # 7) Логируем
    log_event(
        db=db,
        event_type=EventType.PHOTO_UPDATED,
        user_id=current_user.id,
        entity_type=EntityType.PHOTO,
        entity_id="bulk",
        payload={"updates": bulk_data.updates},
        request=request
    )

    return {"message": "Порядок фотографий успешно обновлен"}


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
        request: Request,
        photo_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_photos_write)
):
    """
    Удаление фотографии.

    - **photo_id**: ID фотографии
    """
    # Получаем фотографию из БД
    photo = db.query(ApartmentPhoto).filter(ApartmentPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фотография не найдена"
        )

    # Сохраняем данные для логирования
    photo_data = {
        "id": photo.id,
        "apartment_id": photo.apartment_id,
        "url": photo.url,
        "sort_order": photo.sort_order
    }

    # Пытаемся извлечь image_id из URL для удаления из MinIO
    image_id = None
    if photo.url:
        parts = photo.url.split('/')
        if len(parts) >= 3:
            filename = parts[-1]
            image_id = filename.split('_')[0].split('.')[0]

    # Удаляем запись из БД
    db.delete(photo)
    db.commit()

    # Если нашли image_id, удаляем все варианты из MinIO
    if image_id:
        try:
            minio_service.delete_image(photo.apartment_id, image_id)
        except Exception as e:
            logger.error(f"Error deleting image from MinIO: {e}")

    # Логируем событие
    log_event(
        db=db,
        event_type=EventType.PHOTO_DELETED,
        user_id=current_user.id,
        entity_type=EntityType.PHOTO,
        entity_id=str(photo_id),
        payload=photo_data,
        request=request
    )

    return None
