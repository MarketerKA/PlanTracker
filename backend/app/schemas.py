from pydantic import BaseModel, EmailStr, constr, field_validator
from typing import List, Optional
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

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
    email: str  # Changed from EmailStr to str for custom validation
    
    @field_validator('email')
    def validate_email_field(cls, v):
        try:
            # Strict validation with deliverability check
            valid = validate_email(v, check_deliverability=True)
            
            # Check for common test domains
            domain = v.split('@')[1].lower()
            if domain in ['example.com', 'test.com', 'example.org']:
                raise ValueError(f"Email domain {domain} is not allowed")
                
            # Return normalized email
            return valid.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {str(e)}")

class UserCreate(UserBase):
    password: constr(min_length=8)  # Minimum password length of 8 characters
    
    class Config:
        # This ensures error messages are properly shown
        json_schema_extra = {
            "example": {
                "email": "user@gmail.com",
                "password": "strongpassword123"
            }
        }

class UserUpdate(UserBase):
    telegram_chat_id: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
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