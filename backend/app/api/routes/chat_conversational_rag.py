# backend/api/routes/chat_conversational_rag.py

from fastapi import APIRouter
from pydantic import BaseModel
from chains.conversational_rag_recommender import ConversationalRagRecommender

router = APIRouter()

# Initialize the chatbot
chatbot = ConversationalRagRecommender()

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"


@router.post("/chat-conversational-rag")
def chat_with_rag(msg: ChatMessage):
    """
    Conversation-based chat endpoint using RAG for music recommendations.
    """
    session_id = msg.session_id
    reply = chatbot.ask(msg.message, session_id=session_id)

    # If user confirmed download, also return downloaded file paths
    if any(word in msg.message.lower() for word in ["yes", "sure", "go ahead", "download", "yep"]):
        files = chatbot.download_stored_songs(session_id)
        return {"reply": reply, "downloads": files}

    return {"reply": reply}
