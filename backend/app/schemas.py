from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional
from datetime import datetime

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    tags: List[str] = []

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(ActivityBase):
    end_time: Optional[datetime] = None
    duration: Optional[int] = None

class Activity(ActivityBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    user_id: int
    tags: List[Tag] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: constr(min_length=8)  # Minimum password length of 8 characters

class UserUpdate(UserBase):
    telegram_chat_id: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    telegram_chat_id: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class VerifyEmail(BaseModel):
    email: EmailStr
    verification_code: str 