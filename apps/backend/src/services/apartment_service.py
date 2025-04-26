from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
import logging
import json
from datetime import datetime

from src.models.apartment import Apartment, ApartmentPhoto
from src.schemas.apartment import ApartmentCreate, ApartmentUpdate, ApartmentInList
from src.services.minio_service import MinioService

logger = logging.getLogger(__name__)


class ApartmentService:
    """
    Сервис для работы с квартирами.
    """

    @staticmethod
    def get_apartments(
            db: Session,
            page: int = 1,
            page_size: int = 12,
            sort_field: str = "created_at",
            sort_order: str = "desc"
    ) -> Tuple[List[Apartment], int]:
        """
        Получение списка квартир с пагинацией и сортировкой.

        Args:
            db: Сессия базы данных
            page: Номер страницы
            page_size: Размер страницы
            sort_field: Поле для сортировки
            sort_order: Порядок сортировки (asc/desc)

        Returns:
            Tuple[List[Apartment], int]: Список квартир и общее количество
        """
        try:
            # Определяем поле и порядок сортировки
            sort_column = getattr(Apartment, sort_field)
            if sort_order == "desc":
                sort_column = desc(sort_column)
            else:
                sort_column = asc(sort_column)

            # Получаем общее количество активных квартир
            total = db.query(func.count(Apartment.id)).filter(
                Apartment.active.is_(True)
            ).scalar()

            # Получаем квартиры с пагинацией и сортировкой
            apartments = db.query(Apartment).filter(
                Apartment.active.is_(True)
            ).order_by(
                sort_column
            ).offset(
                (page - 1) * page_size
            ).limit(
                page_size
            ).all()

            return apartments, total

        except Exception as e:
            logger.error(f"Error getting apartments: {e}")
            raise

    @staticmethod
    def get_apartment_by_id(db: Session, apartment_id: int) -> Optional[Apartment]:
        """
        Получение квартиры по ID.

        Args:
            db: Сессия базы данных
            apartment_id: ID квартиры

        Returns:
            Optional[Apartment]: Квартира или None
        """
        try:
            return db.query(Apartment).filter(
                Apartment.id == apartment_id,
                Apartment.active.is_(True)
            ).first()
        except Exception as e:
            logger.error(f"Error getting apartment by ID: {e}")
            raise

    @staticmethod
    def get_apartment_photos(db: Session, apartment_id: int) -> List[ApartmentPhoto]:
        """
        Получение списка фотографий квартиры.

        Args:
            db: Сессия базы данных
            apartment_id: ID квартиры

        Returns:
            List[ApartmentPhoto]: Список фотографий
        """
        try:
            return db.query(ApartmentPhoto).filter(
                ApartmentPhoto.apartment_id == apartment_id
            ).order_by(
                ApartmentPhoto.sort_order
            ).all()
        except Exception as e:
            logger.error(f"Error getting apartment photos: {e}")
            raise

    @staticmethod
    def get_apartment_photos_with_variants(db: Session, apartment_id: int) -> List[Dict]:
        """
        Получение списка фотографий квартиры со всеми вариантами изображений.

        Args:
            db: Сессия базы данных
            apartment_id: ID квартиры

        Returns:
            List[Dict]: Список фотографий с вариантами
        """
        try:
            # Получаем фотографии из БД
            photos = ApartmentService.get_apartment_photos(db, apartment_id)

            # Создаем экземпляр сервиса MinIO
            minio_service = MinioService()

            # Получаем все изображения с вариантами
            images = minio_service.get_apartment_images(apartment_id)

            # Сопоставляем фотографии из БД с изображениями в MinIO
            result = []

            for photo in photos:
                # Пытаемся извлечь image_id из URL
                image_id = None
                if photo.url:
                    # Предполагаем, что URL имеет формат /apartments/{apartment_id}/{image_id}* или подобный
                    parts = photo.url.split('/')
                    if len(parts) >= 3:
                        filename = parts[-1]
                        image_id = filename.split('_')[0].split('.')[0]

                # Если нашли image_id и есть соответствующие варианты
                if image_id and image_id in images:
                    variants = images[image_id]
                    result.append({
                        "id": photo.id,
                        "apartment_id": photo.apartment_id,
                        "sort_order": photo.sort_order,
                        "image_id": image_id,
                        "variants": variants
                    })
                else:
                    # Если не нашли варианты, используем URL из БД
                    result.append({
                        "id": photo.id,
                        "apartment_id": photo.apartment_id,
                        "sort_order": photo.sort_order,
                        "image_id": None,
                        "variants": {"original": photo.url}
                    })

            return result

        except Exception as e:
            logger.error(f"Error getting apartment photos with variants: {e}")
            # В случае ошибки возвращаем фотографии только из БД
            photos = ApartmentService.get_apartment_photos(db, apartment_id)
            return [{
                "id": photo.id,
                "apartment_id": photo.apartment_id,
                "sort_order": photo.sort_order,
                "image_id": None,
                "variants": {"original": photo.url}
            } for photo in photos]

    @staticmethod
    def get_apartment_cover(db: Session, apartment_id: int) -> Optional[str]:
        """
        Получение URL обложки квартиры (первой фотографии).

        Args:
            db: Сессия базы данных
            apartment_id: ID квартиры

        Returns:
            Optional[str]: URL обложки или None
        """
        try:
            photo = db.query(ApartmentPhoto).filter(
                ApartmentPhoto.apartment_id == apartment_id
            ).order_by(
                ApartmentPhoto.sort_order
            ).first()

            return photo.url if photo else None
        except Exception as e:
            logger.error(f"Error getting apartment cover: {e}")
            raise

    @staticmethod
    def get_apartment_cover_with_variants(db: Session, apartment_id: int) -> Dict:
        """
        Получение URL обложки квартиры с вариантами разных размеров.

        Args:
            db: Сессия базы данных
            apartment_id: ID квартиры

        Returns:
            Dict: Словарь с вариантами обложки {size_format: url}
        """
        try:
            # Получаем первую фотографию
            photo = db.query(ApartmentPhoto).filter(
                ApartmentPhoto.apartment_id == apartment_id
            ).order_by(
                ApartmentPhoto.sort_order
            ).first()

            if not photo:
                return {}

            # Пытаемся извлечь image_id из URL
            image_id = None
            if photo.url:
                parts = photo.url.split('/')
                if len(parts) >= 3:
                    filename = parts[-1]
                    image_id = filename.split('_')[0].split('.')[0]

            # Если нашли image_id, получаем варианты
            if image_id:
                minio_service = MinioService()
                variants = minio_service.get_image_variants(apartment_id, image_id)
                return variants

            # Если не нашли варианты, возвращаем только оригинальный URL
            return {"original": photo.url} if photo.url else {}

        except Exception as e:
            logger.error(f"Error getting apartment cover with variants: {e}")
            # В случае ошибки возвращаем только основной URL
            return {"original": ApartmentService.get_apartment_cover(db, apartment_id) or ""}

    @staticmethod
    def add_apartment_photo(
            db: Session,
            apartment_id: int,
            url: str,
            metadata: Optional[Dict] = None
    ) -> ApartmentPhoto:
        """
        Добавление фотографии к квартире.

        Args:
            db: Сессия базы данных
            apartment_id: ID квартиры
            url: URL фотографии
            metadata: Метаданные (вариант, размеры и т.д.)

        Returns:
            ApartmentPhoto: Созданная фотография
        """
        try:
            # Определяем порядок сортировки для нового фото
            max_sort_order = db.query(func.max(ApartmentPhoto.sort_order)).filter(
                ApartmentPhoto.apartment_id == apartment_id
            ).scalar() or -1

            # Создаем запись о фотографии
            new_photo = ApartmentPhoto(
                apartment_id=apartment_id,
                url=url,
                sort_order=max_sort_order + 1,
                metadata=json.dumps(metadata) if metadata else None
            )

            db.add(new_photo)
            db.commit()
            db.refresh(new_photo)

            return new_photo
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding apartment photo: {e}")
            raise

    @staticmethod
    def update_photo_sort_order(
            db: Session,
            photo_id: int,
            new_sort_order: int
    ) -> Optional[ApartmentPhoto]:
        """
        Обновление порядка сортировки фотографии.

        Args:
            db: Сессия базы данных
            photo_id: ID фотографии
            new_sort_order: Новый порядок сортировки

        Returns:
            Optional[ApartmentPhoto]: Обновленная фотография или None
        """
        try:
            # Получаем фотографию
            photo = db.query(ApartmentPhoto).filter(
                ApartmentPhoto.id == photo_id
            ).first()

            if not photo:
                return None

            # Обновляем порядок сортировки
            photo.sort_order = new_sort_order
            db.commit()
            db.refresh(photo)

            return photo
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating photo sort order: {e}")
            raise

    @staticmethod
    def delete_photo(
            db: Session,
            photo_id: int
    ) -> bool:
        """
        Удаление фотографии.

        Args:
            db: Сессия базы данных
            photo_id: ID фотографии

        Returns:
            bool: Успешно или нет
        """
        try:
            # Получаем фотографию
            photo = db.query(ApartmentPhoto).filter(
                ApartmentPhoto.id == photo_id
            ).first()

            if not photo:
                return False

            # Удаляем фотографию из БД
            db.delete(photo)
            db.commit()

            # Пытаемся извлечь image_id из URL для удаления из MinIO
            image_id = None
            if photo.url:
                parts = photo.url.split('/')
                if len(parts) >= 3:
                    filename = parts[-1]
                    image_id = filename.split('_')[0].split('.')[0]

            # Если нашли image_id, удаляем все варианты из MinIO
            if image_id:
                minio_service = MinioService()
                minio_service.delete_image(photo.apartment_id, image_id)

            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting photo: {e}")
            raise

    @staticmethod
    def create_apartment_list_item(
            db: Session,
            apartment: Apartment,
            preferred_variant: str = "small_webp"
    ) -> ApartmentInList:
        """
        Создание элемента списка квартир с обложкой.

        Args:
            db: Сессия базы данных
            apartment: Квартира
            preferred_variant: Предпочтительный вариант изображения

        Returns:
            ApartmentInList: Элемент списка
        """
        try:
            # Получаем варианты обложки
            cover_variants = ApartmentService.get_apartment_cover_with_variants(db, apartment.id)

            # Выбираем предпочтительный вариант или любой доступный
            cover_url = (
                cover_variants.get(preferred_variant) or
                cover_variants.get("small_jpeg") or
                cover_variants.get("original") or
                next(iter(cover_variants.values())) if cover_variants else None
            )

            # Создаем элемент списка
            return ApartmentInList(
                id=apartment.id,
                title=apartment.title,
                price_rub=apartment.price_rub,
                rooms=apartment.rooms,
                floor=apartment.floor,
                area_m2=apartment.area_m2,
                cover_url=cover_url
            )
        except Exception as e:
            logger.error(f"Error creating apartment list item: {e}")
            raise