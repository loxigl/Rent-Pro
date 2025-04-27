from pydantic import BaseModel, EmailStr, Field


class TokenData(BaseModel):
    """Данные, которые кодируются в JWT токене."""
    sub: str  # email пользователя
    role: str
    user_id: int


class Token(BaseModel):
    """Схема ответа с токенами."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Схема запроса для входа."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class RefreshTokenRequest(BaseModel):
    """Схема запроса для обновления токена."""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Схема запроса для изменения пароля."""
    current_password: str
    new_password: str = Field(..., min_length=6)
