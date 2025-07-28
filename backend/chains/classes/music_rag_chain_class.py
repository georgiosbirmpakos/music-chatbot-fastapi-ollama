from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from app.core.config import DEFAULT_MODEL_NAME

class MusicRAGChain:
    def __init__(self, music_data: list[str], model_name: str = DEFAULT_MODEL_NAME):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = FAISS.from_documents(
            [Document(page_content=text) for text in music_data], self.embeddings
        )
        # Use ChatOllama for universal handling (works with both text & chat models)
        self.llm = ChatOllama(model=model_name)

    def recommend_songs(self, query: str, top_k: int = 5):
        docs = self.vectorstore.similarity_search(query, k=top_k * 5)
        seen = set()
        results = []
        for doc in docs:
            parts = dict(item.split(": ", 1) for item in doc.page_content.split(" | "))
            song_key = (parts.get("Title"), parts.get("Artist"))
            if song_key not in seen:
                seen.add(song_key)
                results.append(parts)
            if len(results) >= top_k:
                break
        return "\n".join(f"{i+1}. {s['Artist']} – {s['Title']} ({s['Decade']})" for i, s in enumerate(results))

    def chat(self, message: str):
        response = self.llm.invoke(message)
        return response.content if hasattr(response, "content") else str(response)
