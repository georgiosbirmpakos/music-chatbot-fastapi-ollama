# backend/app/api/routes/chat_conversational_rag.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from chains.conversational_rag_recommender import ConversationalRagRecommender
from chains.music_rag_chain import rag_chain
import logging, traceback

router = APIRouter()
chatbot = ConversationalRagRecommender(rag_chain)

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

@router.post("/chat-conversational-rag")
def chat_with_rag(msg: ChatMessage):
    try:
        reply = chatbot.ask(msg.message, session_id=msg.session_id)
        return {"reply": reply}
    except Exception as e:
        logging.error("chat-conversational-rag failed: %s\n%s", e, traceback.format_exc())
        # In dev, expose message to help debugging:
        raise HTTPException(status_code=500, detail=str(e))
