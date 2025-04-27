from src.schemas.admin.auth import (
    TokenData, Token, LoginRequest, RefreshTokenRequest, ChangePasswordRequest
)
from src.schemas.admin.user import (
    UserBase, UserCreate, UserUpdate, UserResponse, UserWithPermissions, UsersListResponse
)
from src.schemas.admin.apartment import (
    ApartmentAdminBase, ApartmentAdminCreate, ApartmentAdminUpdate, ApartmentAdminDetail,
    ApartmentAdminListItem, ApartmentAdminListResponse
)
from src.schemas.admin.photo import (
    PhotoAdminBase, PhotoAdminCreate, PhotoAdminUpdate, PhotoAdminDetail,
    PhotoAdminListItem, PhotoAdminListResponse, BulkPhotoUpdateRequest, PhotoUploadResponse
)
from src.schemas.admin.event import (
    EventLogDetail, EventLogListResponse, EventLogFilter
)

__all__ = [
    # Auth schemas
    'TokenData', 'Token', 'LoginRequest', 'RefreshTokenRequest', 'ChangePasswordRequest',

    # User schemas
    'UserBase', 'UserCreate', 'UserUpdate', 'UserResponse', 'UserWithPermissions', 'UsersListResponse',

    # Apartment admin schemas
    'ApartmentAdminBase', 'ApartmentAdminCreate', 'ApartmentAdminUpdate', 'ApartmentAdminDetail',
    'ApartmentAdminListItem', 'ApartmentAdminListResponse',

    # Photo admin schemas
    'PhotoAdminBase', 'PhotoAdminCreate', 'PhotoAdminUpdate', 'PhotoAdminDetail',
    'PhotoAdminListItem', 'PhotoAdminListResponse', 'BulkPhotoUpdateRequest', 'PhotoUploadResponse',

    # Event log schemas
    'EventLogDetail', 'EventLogListResponse', 'EventLogFilter'
]
