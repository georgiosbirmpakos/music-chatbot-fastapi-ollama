from fastapi import APIRouter
from app.api.routes import recommend, chat

router = APIRouter()
router.include_router(recommend.router)
router.include_router(chat.router)