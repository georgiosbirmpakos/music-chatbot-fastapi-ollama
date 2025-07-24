from fastapi import APIRouter
from app.api.routes import recommend, chat, chat_rag

router = APIRouter()
router.include_router(recommend.router)
router.include_router(chat.router)
router.include_router(chat_rag.router, prefix="", tags=["chat-rag"])
router.include_router(chat_rag.router, prefix="", tags=["chat-rag-recommend"])
