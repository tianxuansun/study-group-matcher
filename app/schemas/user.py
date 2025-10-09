from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)

class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
