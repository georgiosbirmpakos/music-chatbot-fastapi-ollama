# app/core/app_builder.py
from fastapi import FastAPI
from app.api.routes import router

def create_app() -> FastAPI:
    app = FastAPI(title="🎵 Music Chatbot")
    app.include_router(router)
    return app
