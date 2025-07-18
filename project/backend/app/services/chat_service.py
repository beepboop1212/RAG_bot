# backend/app/services/chat_service.py
from sqlalchemy.orm import Session
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage, AIMessage
from fastapi import Depends # Ensure Depends is imported

from backend.app.db import crud
from backend.app import schemas
from backend.app.core.config import settings
from backend.app.db.database import get_db # <--- CORRECT: Import get_db from database.py

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.GOOGLE_API_KEY,
        )

    def _load_chat_history_for_langchain(self, session_id: int) -> ConversationBufferMemory:
        messages_db = crud.get_messages_by_session(self.db, session_id=session_id, limit=50)
        memory = ConversationBufferMemory(return_messages=True)
        for msg_db in messages_db:
            if msg_db.sender_type == "user":
                memory.chat_memory.add_user_message(msg_db.content)
            elif msg_db.sender_type == "ai":
                memory.chat_memory.add_ai_message(msg_db.content)
        return memory

    # def process_user_message(self, session_id: int, user_message_content: str) -> schemas.message.ChatMessage:
    #     user_msg_to_save = schemas.message.ChatMessageCreateInternal(
    #         session_id=session_id,
    #         sender_type="user",
    #         content=user_message_content
    #     )
    #     crud.create_chat_message(self.db, message=user_msg_to_save)

    #     memory = self._load_chat_history_for_langchain(session_id)
    #     conversation = ConversationChain(
    #         llm=self.llm,
    #         memory=memory,
    #         verbose=True
    #     )
    #     ai_response_content = conversation.predict(input=user_message_content)

    #     ai_msg_to_save = schemas.message.ChatMessageCreateInternal(
    #         session_id=session_id,
    #         sender_type="ai",
    #         content=ai_response_content
    #     )
    #     db_ai_message = crud.create_chat_message(self.db, message=ai_msg_to_save)
    #     # return schemas.message.ChatMessage.from_orm(db_ai_message) Pydantic v1
    #     return schemas.message.ChatMessage.model_validate(db_ai_message) # Pydantic v2
# backend/app/services/chat_service.py
# ...
    def process_user_message(self, session_id: int, user_message_content: str) -> schemas.message.ChatMessage:
        print(f"[CHAT_SERVICE] process_user_message called for session_id: {session_id}, content: '{user_message_content}'") # DEBUG

        # 1. Save user message
        user_msg_to_save = schemas.message.ChatMessageCreateInternal(
            session_id=session_id,
            sender_type="user",
            content=user_message_content
        )
        print(f"[CHAT_SERVICE] Attempting to save user message: {user_msg_to_save.model_dump_json()}") # DEBUG (Pydantic V2)
        try:
            db_user_message = crud.create_chat_message(self.db, message=user_msg_to_save)
            print(f"[CHAT_SERVICE] User message saved to DB. ID: {db_user_message.id}, Content: {db_user_message.content[:50]}") # DEBUG
        except Exception as e:
            print(f"[CHAT_SERVICE] ERROR saving user message to DB: {e}") # DEBUG
            # Re-raise or handle appropriately. If this fails, the rest won't proceed.
            raise  # Re-raise the exception to be caught by the endpoint

        # ... (rest of the LLM interaction) ...
        print("[CHAT_SERVICE] Loading chat history...") # DEBUG
        memory = self._load_chat_history_for_langchain(session_id)
        # print(f"[CHAT_SERVICE] Memory loaded: {memory.chat_memory.messages}") # DEBUG - can be verbose

        print("[CHAT_SERVICE] Calling LLM...") # DEBUG
        conversation = ConversationChain(
            llm=self.llm,
            memory=memory,
            verbose=True # Keep this True for now
        )
        
        try:
            ai_response_content = conversation.predict(input=user_message_content)
            print(f"[CHAT_SERVICE] LLM response received: {ai_response_content[:100]}") # DEBUG
        except Exception as e:
            print(f"[CHAT_SERVICE] ERROR during LLM conversation.predict: {e}") # DEBUG
            raise # Re-raise to be caught by endpoint

        # 4. Save AI response
        ai_msg_to_save = schemas.message.ChatMessageCreateInternal(
            session_id=session_id,
            sender_type="ai",
            content=ai_response_content
        )
        print(f"[CHAT_SERVICE] Attempting to save AI message: {ai_msg_to_save.model_dump_json()}") # DEBUG
        try:
            db_ai_message = crud.create_chat_message(self.db, message=ai_msg_to_save)
            print(f"[CHAT_SERVICE] AI message saved to DB. ID: {db_ai_message.id}, Content: {db_ai_message.content[:50]}") # DEBUG
        except Exception as e:
            print(f"[CHAT_SERVICE] ERROR saving AI message to DB: {e}") # DEBUG
            raise # Re-raise

        return schemas.message.ChatMessage.model_validate(db_ai_message)

# Dependency to get ChatService instance
def get_chat_service(db: Session = Depends(get_db)): # <--- CORRECT: Use get_db imported from database.py
    return ChatService(db=db)