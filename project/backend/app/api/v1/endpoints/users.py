# backend/app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from backend.app import schemas       # This imports the 'schemas' package
from backend.app.db import crud       # This imports the 'crud.py' module from 'db'
from backend.app.db.database import get_db # This imports 'get_db' from 'database.py'

router = APIRouter()

@router.post("/login", response_model=schemas.user.User)
def login_or_create_user(
    *,
    db: Session = Depends(get_db), # <--- get_db is used here as a dependency
    user_in: schemas.user.UserCreate
) -> Any:
    user = crud.get_user_by_name_and_topic(db, name=user_in.name, topic=user_in.topic_of_interest) # crud functions use the 'db' session
    if not user:
        user = crud.create_user(db=db, user=user_in) # crud functions use the 'db' session
    return user

@router.get("/{user_id}", response_model=schemas.user.User) # Access User schema via schemas.user
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
) -> Any:
    """
    Get user by ID.
    """
    user = crud.get_user(db, user_id=user_id) # Call functions directly from 'crud' module
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user