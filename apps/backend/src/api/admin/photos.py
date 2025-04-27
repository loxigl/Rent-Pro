from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import Optional, List
import logging

from src.db.database import get_db
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


@router.post("/{apartment_id}/upload", response_model=PhotoUploadResponse)
async def upload_photo(
        request: Request,
        apartment_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(require_photos_write)
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

    # Проверяем формат файла
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поддерживаются только форматы JPEG, PNG и WebP"
        )

    try:
        # Читаем содержимое файла
        file_content = await file.read()

        # Определяем порядок сортировки для нового фото
        max_sort_order = db.query(func.max(ApartmentPhoto.sort_order)).filter(
            ApartmentPhoto.apartment_id == apartment_id
        ).scalar()

        # Если нет фотографий, начинаем с 0, иначе следующий порядок
        new_sort_order = 0 if max_sort_order is None else max_sort_order + 1

        # Загружаем изображение через Celery и получаем URL
        cover_url = process_image.delay(file_content, apartment_id).get()

        # Создаем запись о фотографии
        photo_metadata = {
            "original_filename": file.filename,
            "content_type": file.content_type,
            "is_cover": new_sort_order == 0  # Первое фото - обложка
        }

        # Добавляем фото в БД
        new_photo = ApartmentPhoto(
            apartment_id=apartment_id,
            url=cover_url,
            sort_order=new_sort_order,
            photo_metadata=photo_metadata
        )

        db.add(new_photo)
        db.commit()
        db.refresh(new_photo)

        # Логируем событие
        await log_event(
            db=db,
            event_type=EventType.PHOTO_UPLOADED,
            user_id=current_user.id,
            entity_type=EntityType.PHOTO,
            entity_id=str(new_photo.id),
            payload={
                "apartment_id": apartment_id,
                "filename": file.filename,
                "sort_order": new_sort_order
            },
            request=request
        )

        # Готовим ответ
        return PhotoUploadResponse(
            id=new_photo.id,
            url=cover_url,
            thumbnail_url=cover_url,  # В будущем здесь может быть URL миниатюры
            apartment_id=apartment_id,
            sort_order=new_sort_order,
            is_cover=new_sort_order == 0
        )

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
    await log_event(
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
    Массовое обновление порядка фотографий.

    - **bulk_data**: Массив обновлений {id, sort_order}
    """
    # Собираем IDs всех фотографий для проверки
    photo_ids = [update.get("id") for update in bulk_data.updates]

    # Получаем все фотографии одним запросом
    photos = db.query(ApartmentPhoto).filter(ApartmentPhoto.id.in_(photo_ids)).all()

    # Создаем словарь для быстрого доступа
    photo_dict = {photo.id: photo for photo in photos}

    # Проверяем, что все фотографии найдены
    if len(photos) != len(photo_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некоторые фотографии не найдены"
        )

    # Применяем обновления
    for update in bulk_data.updates:
        photo_id = update.get("id")
        sort_order = update.get("sort_order")

        if photo_id in photo_dict and sort_order is not None:
            photo_dict[photo_id].sort_order = sort_order

    # Сохраняем изменения в БД
    db.commit()

    # Логируем событие
    await log_event(
        db=db,
        event_type=EventType.PHOTO_UPDATED,
        user_id=current_user.id,
        entity_type=EntityType.PHOTO,
        entity_id="bulk",
        payload={
            "updates": bulk_data.updates
        },
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
    await log_event(
        db=db,
        event_type=EventType.PHOTO_DELETED,
        user_id=current_user.id,
        entity_type=EntityType.PHOTO,
        entity_id=str(photo_id),
        payload=photo_data,
        request=request
    )

    return None
