from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Базовая схема пользователя."""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = Field(..., pattern="^(owner|manager)$")


class UserCreate(UserBase):
    """Схема для создания пользователя."""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """Схема для обновления данных пользователя."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(owner|manager)$")
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Схема ответа с информацией о пользователе."""
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserWithPermissions(UserResponse):
    """Схема ответа с информацией о пользователе и его разрешениях."""
    permissions: List[str]


class UsersListResponse(BaseModel):
    """Схема ответа со списком пользователей."""
    items: List[UserResponse]
    total: int
