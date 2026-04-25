from enum import StrEnum

from pydantic import BaseModel, EmailStr


class AppRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class UserRead(BaseModel):
    id: str
    email: EmailStr
    role: AppRole
