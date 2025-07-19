from fastapi import FastAPI
from app.api.router import router

def create_app() -> FastAPI:
    app = FastAPI(title="🎵 Music Chatbot")
    app.include_router(router)
    return app
