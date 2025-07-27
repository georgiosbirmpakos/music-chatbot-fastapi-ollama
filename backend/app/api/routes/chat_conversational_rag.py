from fastapi import APIRouter
from pydantic import BaseModel
from chains.conversational_rag_recommender import ConversationalRagRecommender

router = APIRouter()
chatbot = ConversationalRagRecommender()

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

@router.post("/chat-conversational-rag")
def chat_with_rag(msg: ChatMessage):
    """
    Conversation-based chat endpoint using RAG for music recommendations.
    """
    reply = chatbot.ask(msg.message, session_id=msg.session_id)
    return {"reply": reply}
