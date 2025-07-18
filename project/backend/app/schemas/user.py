# backend/app/schemas/user.py
from pydantic import BaseModel
from typing import Optional
import datetime

# Base model for common attributes
class UserBase(BaseModel):
    name: str
    topic_of_interest: str

# Schema for creating a user (request)
class UserCreate(UserBase):
    pass

# Schema for reading/returning a user (response)
class User(UserBase):
    id: int
    created_at: datetime.datetime

    class Config:
        # orm_mode = True # for Pydantic V1
        from_attributes = True # for Pydantic V2