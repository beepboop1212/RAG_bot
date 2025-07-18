# backend/app/schemas/message.py
from pydantic import BaseModel
import datetime

class ChatMessageBase(BaseModel):
    content: str

# Schema for CREATING a message (request from user to the chat endpoint)
# The client (frontend) will only send the 'content'.
# 'sender_type' will be set by the backend service.
class ChatMessageCreate(ChatMessageBase): # <--- THIS IS THE KEY SCHEMA
    pass # It inherits 'content' from ChatMessageBase. No other fields are required from the client.

# Schema for INTERNAL creation (includes session_id and sender_type)
# This is used by crud.create_chat_message after the service has determined sender_type etc.
class ChatMessageCreateInternal(ChatMessageBase):
    session_id: int
    sender_type: str # "user" or "ai"

# Schema for reading/returning a message (response)
class ChatMessage(ChatMessageBase):
    id: int
    session_id: int
    sender_type: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True # Pydantic V2 (or orm_mode=True for V1)