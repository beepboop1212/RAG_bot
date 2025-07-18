# backend/app/db/crud.py
from sqlalchemy.orm import Session
from . import models
from ..schemas import user as user_schemas
from ..schemas import session as session_schemas
from ..schemas import message as message_schemas # Will use later

from backend.app.db import models
from backend.app import schemas

# --- User CRUD ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_name_and_topic(db: Session, name: str, topic: str):
    return db.query(models.User).filter(models.User.name == name, models.User.topic_of_interest == topic).first()

def create_user(db: Session, user: user_schemas.UserCreate):
    db_user = models.User(name=user.name, topic_of_interest=user.topic_of_interest)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- ChatSession CRUD (Basic stubs for now) ---
def get_session(db: Session, session_id: int):
    return db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()

def get_sessions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ChatSession).filter(models.ChatSession.user_id == user_id).offset(skip).limit(limit).all()

def create_chat_session(db: Session, session: schemas.session.ChatSessionCreate, user_id: int):
    db_session = models.ChatSession(**session.model_dump(), user_id=user_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# --- ChatMessage CRUD (Basic stubs for now) ---
# def create_chat_message(db: Session, message: schemas.message.ChatMessageCreateInternal):
#     db_message = models.ChatMessage(
#         session_id=message.session_id,
#         sender_type=message.sender_type,
#         content=message.content
#     )
#     db.add(db_message)
#     db.commit()
#     db.refresh(db_message)
#     return db_message
# backend/app/db/crud.py
# ...
def create_chat_message(db: Session, message: schemas.message.ChatMessageCreateInternal) -> models.ChatMessage:
    print(f"[CRUD] create_chat_message called. Session ID: {message.session_id}, Sender: {message.sender_type}, Content: {message.content[:50]}") # DEBUG
    try:
        db_message = models.ChatMessage(
            session_id=message.session_id,
            sender_type=message.sender_type,
            content=message.content
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        print(f"[CRUD] Message committed to DB. ID: {db_message.id}") # DEBUG
        return db_message
    except Exception as e:
        print(f"[CRUD] ERROR during DB commit for chat message: {e}") # DEBUG
        db.rollback() # Rollback on error
        raise # Re-raise

def get_messages_by_session(db: Session, session_id: int, skip: int = 0, limit: int = 1000):
    return db.query(models.ChatMessage)\
             .filter(models.ChatMessage.session_id == session_id)\
             .order_by(models.ChatMessage.timestamp.asc())\
             .offset(skip)\
             .limit(limit)\
             .all()

# backend/app/db/crud.py
def create_chat_session(db: Session, session_create: schemas.session.ChatSessionCreate, user_id: int):
    db_session = models.ChatSession(
        user_id=user_id, # User ID comes from path param passed to this function
        session_name=session_create.session_name # session_name from the Pydantic model
    )
    # ...
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_sessions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ChatSession)\
             .filter(models.ChatSession.user_id == user_id)\
             .order_by(models.ChatSession.created_at.desc())\
             .offset(skip)\
             .limit(limit)\
             .all()