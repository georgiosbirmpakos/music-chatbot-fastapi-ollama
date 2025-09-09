# app/api/router.py
from fastapi import APIRouter

# Import sub-routers; each must define `router = APIRouter(...)`
from app.api.routes.chat_conversational_rag import router as chat_router
from app.api.routes.diag import router as diag_router

router = APIRouter()
router.include_router(chat_router, prefix="", tags=["chat"])
router.include_router(diag_router,  prefix="/diag", tags=["diag"])
