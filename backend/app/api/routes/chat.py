from fastapi import APIRouter
from pydantic import BaseModel
from chains.conversational_recommender import ConversationalRecommender

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

chatbot = ConversationalRecommender()

@router.post("/chat")
def chat_with_bot(msg: ChatMessage):
    session_id = msg.session_id
    response = chatbot.ask(msg.message, session_id=session_id)

    if "download" in msg.message.lower() or "yes" in msg.message.lower():
        files = chatbot.download_stored_songs(session_id)
        return {"reply": response, "downloads": files}

    return {"reply": response}



