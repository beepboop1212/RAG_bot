# backend/app/api/v1/api.py
from fastapi import APIRouter
from .endpoints import users, sessions, chat # Make sure chat is imported

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(sessions.router, tags=["Chat Sessions"]) # No prefix for sessions router
api_router.include_router(chat.router, tags=["Chat Messages"])    # No prefix, paths are /sessions/{id}/messages