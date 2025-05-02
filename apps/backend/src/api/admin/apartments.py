from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Path
from sqlalchemy.orm import Session, AsyncSession
from sqlalchemy import func, desc, asc, select
from typing import Optional, List
import logging

from src.db.database import get_db
from src.models.apartment import Apartment, ApartmentPhoto
from src.models.auth import User
from src.models.event_log import EventType, EntityType
from src.schemas.admin import (
    ApartmentAdminCreate, ApartmentAdminUpdate, ApartmentAdminDetail,
    ApartmentAdminListResponse, ApartmentAdminListItem
)
from src.middleware.auth import get_current_active_user
from src.middleware.acl import require_apartments_read, require_apartments_write
from src.services.event_log_service import log_event, log_action
from src.models.role import RolePermission

router = APIRouter(prefix="/apartments", tags=["admin-apartments"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ApartmentAdminListResponse)
async def get_apartments(
        search: Optional[str] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        sort: str = Query("created_at", regex="^(created_at|price_rub|title)$"),
        order: str = Query("desc", regex="^(asc|desc)$"),
        active_only: bool = False,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_apartments_read)
):
    """
    Получение списка квартир для админ-панели с возможностью поиска и фильтрации.

    - **search**: Поисковый запрос (ищет в заголовке и адресе)
    - **page**: Номер страницы
    - **page_size**: Размер страницы
    - **sort**: Поле для сортировки (created_at, price_rub, title)
    - **order**: Порядок сортировки (asc, desc)
    - **active_only**: Показывать только активные квартиры
    """
    # Формируем запрос
    query = db.query(Apartment)

    # Фильтрация по активности
    if active_only:
        query = query.filter(Apartment.active.is_(True))

    # Поиск по заголовку и адресу
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Apartment.title.ilike(search_term)) |
            (Apartment.address.ilike(search_term))
        )

    # Получаем общее количество квартир
    total = query.count()

    # Определяем порядок сортировки
    sort_column = getattr(Apartment, sort)
    if order == "desc":
        sort_column = desc(sort_column)
    else:
        sort_column = asc(sort_column)

    # Применяем сортировку и пагинацию
    apartments = query.order_by(
        sort_column
    ).offset(
        (page - 1) * page_size
    ).limit(
        page_size
    ).all()

    # Подготавливаем результат
    items = []
    for apartment in apartments:
        # Получаем количество фотографий
        photos_count = db.query(func.count(ApartmentPhoto.id)).filter(
            ApartmentPhoto.apartment_id == apartment.id
        ).scalar()

        # Получаем URL обложки (если есть)
        cover_photo = db.query(ApartmentPhoto).filter(
            ApartmentPhoto.apartment_id == apartment.id
        ).order_by(
            ApartmentPhoto.sort_order
        ).first()

        cover_url = cover_photo.url if cover_photo else None

        # Создаем элемент списка
        item = ApartmentAdminListItem(
            id=apartment.id,
            title=apartment.title,
            price_rub=apartment.price_rub,
            rooms=apartment.rooms,
            area_m2=apartment.area_m2,
            active=apartment.active,
            photos_count=photos_count,
            cover_url=cover_url,
            created_at=apartment.created_at
        )

        items.append(item)

    return ApartmentAdminListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{apartment_id}", response_model=ApartmentAdminDetail)
async def get_apartment(
        apartment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_apartments_read)
):
    """
    Получение детальной информации о квартире по ID.

    - **apartment_id**: ID квартиры
    """
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()

    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Квартира не найдена"
        )

    # Получаем количество фотографий
    photos_count = db.query(func.count(ApartmentPhoto.id)).filter(
        ApartmentPhoto.apartment_id == apartment.id
    ).scalar()

    # Создаем результат
    result = ApartmentAdminDetail(
        id=apartment.id,
        title=apartment.title,
        price_rub=apartment.price_rub,
        rooms=apartment.rooms,
        floor=apartment.floor,
        area_m2=apartment.area_m2,
        address=apartment.address,
        description=apartment.description,
        active=apartment.active,
        photos_count=photos_count,
        created_at=apartment.created_at,
        updated_at=apartment.updated_at
    )

    return result


@router.post("", response_model=ApartmentAdminDetail, status_code=status.HTTP_201_CREATED)
async def create_apartment(
        request: Request,
        apartment_data: ApartmentAdminCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_apartments_write)
):
    """
    Создание новой квартиры.

    - **apartment_data**: Данные для создания квартиры
    """
    # Проверяем уникальность заголовка
    existing = db.query(Apartment).filter(Apartment.title == apartment_data.title).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Квартира с таким заголовком уже существует"
        )

    # Создаем новую квартиру
    apartment = Apartment(**apartment_data.model_dump())

    # Сохраняем в БД
    db.add(apartment)
    db.commit()
    db.refresh(apartment)

    # Логируем событие создания квартиры
    await log_event(
        db=db,
        event_type=EventType.APARTMENT_CREATED,
        user_id=current_user.id,
        entity_type=EntityType.APARTMENT,
        entity_id=str(apartment.id),
        payload=apartment_data.model_dump(),
        request=request
    )

    # Получаем количество фотографий (в новой квартире их нет)
    photos_count = 0

    # Создаем результат
    result = ApartmentAdminDetail(
        id=apartment.id,
        title=apartment.title,
        price_rub=apartment.price_rub,
        rooms=apartment.rooms,
        floor=apartment.floor,
        area_m2=apartment.area_m2,
        address=apartment.address,
        description=apartment.description,
        active=apartment.active,
        photos_count=photos_count,
        created_at=apartment.created_at,
        updated_at=apartment.updated_at
    )

    return result


@router.patch("/{apartment_id}", response_model=ApartmentAdminDetail)
async def update_apartment(
        request: Request,
        apartment_id: int,
        apartment_data: ApartmentAdminUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_apartments_write)
):
    """
    Обновление данных квартиры.

    - **apartment_id**: ID квартиры
    - **apartment_data**: Данные для обновления квартиры
    """
    # Получаем квартиру из БД
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()

    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Квартира не найдена"
        )

    # Проверяем уникальность заголовка, если он изменяется
    if apartment_data.title is not None and apartment_data.title != apartment.title:
        existing = db.query(Apartment).filter(Apartment.title == apartment_data.title).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Квартира с таким заголовком уже существует"
            )

    # Сохраняем предыдущее состояние для логирования
    previous_state = {
        "title": apartment.title,
        "price_rub": apartment.price_rub,
        "rooms": apartment.rooms,
        "floor": apartment.floor,
        "area_m2": apartment.area_m2,
        "address": apartment.address,
        "description": apartment.description,
        "active": apartment.active
    }

    # Обновляем данные квартиры
    update_data = apartment_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(apartment, key, value)

    # Сохраняем изменения в БД
    db.commit()
    db.refresh(apartment)

    # Логируем событие обновления квартиры
    await log_event(
        db=db,
        event_type=EventType.APARTMENT_UPDATED,
        user_id=current_user.id,
        entity_type=EntityType.APARTMENT,
        entity_id=str(apartment.id),
        payload={
            "previous": previous_state,
            "current": update_data
        },
        request=request
    )

    # Получаем количество фотографий
    photos_count = db.query(func.count(ApartmentPhoto.id)).filter(
        ApartmentPhoto.apartment_id == apartment.id
    ).scalar()

    # Создаем результат
    result = ApartmentAdminDetail(
        id=apartment.id,
        title=apartment.title,
        price_rub=apartment.price_rub,
        rooms=apartment.rooms,
        floor=apartment.floor,
        area_m2=apartment.area_m2,
        address=apartment.address,
        description=apartment.description,
        active=apartment.active,
        photos_count=photos_count,
        created_at=apartment.created_at,
        updated_at=apartment.updated_at
    )

    return result


@router.delete("/{apartment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_apartment(
        request: Request,
        apartment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_apartments_write)
):
    """
    Удаление квартиры.

    - **apartment_id**: ID квартиры
    """
    # Получаем квартиру из БД
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()

    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Квартира не найдена"
        )

    # Сохраняем данные для логирования
    apartment_data = {
        "id": apartment.id,
        "title": apartment.title,
        "price_rub": apartment.price_rub,
        "rooms": apartment.rooms,
        "floor": apartment.floor,
        "area_m2": apartment.area_m2,
        "address": apartment.address,
        "active": apartment.active
    }

    # Удаляем все фотографии квартиры
    db.query(ApartmentPhoto).filter(ApartmentPhoto.apartment_id == apartment_id).delete()

    # Удаляем квартиру
    db.delete(apartment)
    db.commit()

    # Логируем событие удаления квартиры
    await log_event(
        db=db,
        event_type=EventType.APARTMENT_DELETED,
        user_id=current_user.id,
        entity_type=EntityType.APARTMENT,
        entity_id=str(apartment_id),
        payload=apartment_data,
        request=request
    )

    return None


@router.patch("/{apartment_id}/booking-toggle", response_model=dict)
async def toggle_apartment_booking(
    apartment_id: int = Path(..., description="ID квартиры"),
    enable: bool = Query(True, description="Включить или отключить бронирование"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user(required_permissions=RolePermission.MANAGE_APARTMENTS))
):
    """
    Включить/отключить возможность бронирования для конкретной квартиры.
    """
    # Проверяем наличие квартиры
    apartment_query = select(Apartment).where(Apartment.id == apartment_id)
    result = await db.execute(apartment_query)
    apartment = result.scalars().first()
    
    if not apartment:
        raise HTTPException(
            status_code=404,
            detail=f"Квартира с ID {apartment_id} не найдена"
        )
    
    # Обновляем поле booking_enabled
    apartment.booking_enabled = enable
    
    # Логируем изменение
    action = "включена" if enable else "отключена"
    await log_action(
        db=db,
        entity_type=EntityType.APARTMENT,
        entity_id=apartment_id,
        event_type=EventType.APARTMENT_UPDATED,
        description=f"Возможность бронирования для квартиры #{apartment_id} {action} пользователем {current_user.get('username')}",
        user_id=current_user.get('id'),
        ip_address=None,
        user_agent=None,
        payload={"booking_enabled": enable}
    )
    
    await db.commit()
    
    return {
        "apartment_id": apartment_id,
        "booking_enabled": enable,
        "message": f"Возможность бронирования для квартиры {apartment_id} успешно {'включена' if enable else 'отключена'}"
    }
