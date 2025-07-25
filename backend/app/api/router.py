from fastapi import APIRouter
from app.api.routes import chat, chat_conversational_rag

router = APIRouter()
router.include_router(chat.router, prefix="", tags=["chat"])
router.include_router(chat_conversational_rag.router, prefix="", tags=["chat-conversational-rag"])
