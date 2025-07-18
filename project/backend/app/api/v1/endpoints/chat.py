# backend/app/api/v1/endpoints/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from backend.app import schemas
from backend.app.db import crud # For direct DB access if needed, though service handles most
from backend.app.db.database import get_db
from backend.app.services.chat_service import ChatService, get_chat_service # Import service

router = APIRouter()

# @router.post("/sessions/{session_id}/messages", response_model=schemas.message.ChatMessage)
# def send_message_to_session(
#     *,
#     session_id: int,
#     message_in: schemas.message.ChatMessageCreate, # User only sends content
#     # db: Session = Depends(get_db), # ChatService will get its own db session
#     chat_service: ChatService = Depends(get_chat_service) # Use the service
# ) -> Any:
#     """
#     Send a message from a user to a specific chat session.
#     The AI's response will be returned.
#     """
#     # Verify session exists (optional, ChatService could also handle or raise error)
#     # session = crud.get_session(db, session_id=session_id) # db would be needed here
#     # if not session:
#     #     raise HTTPException(status_code=404, detail="Session not found")

#     # The ChatService will handle saving the user message, calling LLM, and saving AI response
#     ai_response_message = chat_service.process_user_message(
#         session_id=session_id,
#         user_message_content=message_in.content
#     )
#     return ai_response_message
# backend/app/api/v1/endpoints/chat.py
# ...
@router.post("/sessions/{session_id}/messages", response_model=schemas.message.ChatMessage)
def send_message_to_session(
    *,
    session_id: int,
    message_in: schemas.message.ChatMessageCreate,
    chat_service: ChatService = Depends(get_chat_service)
) -> Any:
    print(f"[ENDPOINT_CHAT] Received POST to /sessions/{session_id}/messages") # DEBUG
    print(f"[ENDPOINT_CHAT] Message content from user: '{message_in.content}'") # DEBUG
    
    # Optional: Verify session exists here if you suspect session_id issues
    # from backend.app.db.database import SessionLocal # Temp for direct check
    # temp_db = SessionLocal()
    # session_check = crud.get_session(temp_db, session_id=session_id)
    # print(f"[ENDPOINT_CHAT] Session check for ID {session_id}: {session_check}")
    # temp_db.close()
    # if not session_check:
    #     print(f"[ENDPOINT_CHAT] Session {session_id} not found!")
    #     raise HTTPException(status_code=404, detail="Session not found from endpoint check")

    try:
        ai_response_message = chat_service.process_user_message(
            session_id=session_id,
            user_message_content=message_in.content
        )
        print(f"[ENDPOINT_CHAT] AI response generated: {ai_response_message.content[:50] if ai_response_message else 'None'}") # DEBUG
        return ai_response_message
    except Exception as e:
        print(f"[ENDPOINT_CHAT] Error during chat_service.process_user_message: {e}") # DEBUG
        # Consider raising an HTTPException here to inform the client
        raise HTTPException(status_code=500, detail=f"Internal server error processing message: {str(e)}")
    

@router.get("/sessions/{session_id}/messages", response_model=List[schemas.message.ChatMessage])
def get_session_messages(
    *,
    db: Session = Depends(get_db),
    session_id: int,
    skip: int = 0,
    limit: int = 100 # Client can request more if pagination is implemented
) -> Any:
    """
    Retrieve all messages for a specific chat session.
    """
    # Verify session exists
    session = crud.get_session(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = crud.get_messages_by_session(db, session_id=session_id, skip=skip, limit=limit)
    return messages