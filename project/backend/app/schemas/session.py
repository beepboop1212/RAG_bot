# backend/app/schemas/session.py
from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

class ChatSessionBase(BaseModel):
    session_name: Optional[str] = Field(default="New Chat", examples=["My Gemini Project"])

class ChatSessionCreate(ChatSessionBase): # <--- THIS CLASS DEFINITION
    pass

class ChatSessionUpdate(ChatSessionBase):
    pass

class ChatSession(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True