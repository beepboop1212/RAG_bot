# backend/app/api/v1/endpoints/sessions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from backend.app import schemas
from backend.app.db import crud
from backend.app.db.database import get_db

router = APIRouter()

@router.post("/users/{user_id}/sessions", response_model=schemas.session.ChatSession, status_code=status.HTTP_201_CREATED)
def create_new_session(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    session_in: schemas.session.ChatSessionCreate
) -> Any:
    """
    Create a new chat session for a user.
    The user_id is taken from the path.
    session_in can optionally provide a session_name.
    """
    # Verify user exists (optional, but good practice)
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    # The session_in schema (ChatSessionCreate) now only needs 'session_name' (optional)
    # The 'user_id' for the session is taken from the path parameter.
    return crud.create_chat_session(db=db, session_create=session_in, user_id=user_id)


@router.get("/users/{user_id}/sessions", response_model=List[schemas.session.ChatSession])
def list_user_sessions(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve all chat sessions for a specific user.
    """
    # Verify user exists (optional)
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    sessions = crud.get_sessions_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return sessions

@router.get("/{session_id}", response_model=schemas.session.ChatSession)
def get_session_details( # Renamed for clarity from original get_session
    *,
    db: Session = Depends(get_db),
    session_id: int
) -> Any:
    """
    Retrieve details for a specific session.
    """
    session = crud.get_session(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session with id {session_id} not found")
    return session

# Optional: Add delete endpoint later if needed
# @router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_session(...):

@router.post("/users/{user_id}/sessions", response_model=schemas.session.ChatSession, status_code=status.HTTP_201_CREATED)
def create_new_session_for_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,  # user_id from path
    session_in: schemas.session.ChatSessionCreate # Request body
) -> Any:
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return crud.create_chat_session(db=db, session_create=session_in, user_id=user_id) # user_id passed to CRUD