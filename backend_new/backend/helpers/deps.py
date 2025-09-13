# backend/helpers/deps.py
from fastapi import Request
from openai import OpenAI
from backend.classes import MusicBrainzClient

def get_mb_client(request: Request) -> MusicBrainzClient:
    return request.app.state.mb_client

def get_openai_client(request: Request) -> OpenAI:
    return request.app.state.openai_client
