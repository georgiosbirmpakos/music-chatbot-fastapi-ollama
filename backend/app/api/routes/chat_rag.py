from fastapi import APIRouter
from pydantic import BaseModel
from chains.music_rag_chain import rag_chain
from fastapi.responses import PlainTextResponse

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    top_k: int = 5
    
@router.post("/chat-rag")
def chat_rag(request: ChatRequest):
    """
    Chat endpoint using RAG with Ollama model and music dataset.
    """
    response = rag_chain.run_query(request.question)
    answer = response["answer"] if "answer" in response else str(response)
    return {"answer": answer, "chat_history": [msg.content for msg in response["chat_history"]]}

@router.post("/chat-rag-recommend", response_class=PlainTextResponse)
def recommend(request: ChatRequest):
    return rag_chain.recommend_songs(request.question, top_k=request.top_k)