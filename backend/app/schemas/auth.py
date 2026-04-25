from enum import Enum

from pydantic import BaseModel, EmailStr


class AppRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserRead(BaseModel):
    id: str
    email: EmailStr
    role: AppRole
