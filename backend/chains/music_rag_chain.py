# backend/chains/music_rag_chain.py

from langchain.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document
from app.core.config import DEFAULT_MODEL_NAME
import os
import json
from fastapi.responses import PlainTextResponse


def load_music_dataset(dataset_path: str):
    """Loads JSON dataset with real songs."""
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        songs = json.load(f)

    # Convert each song into simple text for embeddings
    music_texts = []
    for song in songs:
        text = (
            f"Title: {song['title']} | Artist: {song['artist']} | Mood: {song['mood']} | "
            f"Genre: {song['genre']} | Year: {song['year']} | Lyrics: {song['lyrics']}"
        )
        music_texts.append(text)
    return music_texts



class MusicRAGChain:
    def __init__(self, music_data: list[str], model_name: str = DEFAULT_MODEL_NAME):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = self._build_vectorstore(music_data)
        self.llm = Ollama(model=model_name)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(),
            memory=self.memory
        )

    def _build_vectorstore(self, music_data: list[str]):
        docs = [Document(page_content=text) for text in music_data]
        return FAISS.from_documents(docs, self.embeddings)
    
    def recommend_songs(self, query: str, top_k: int = 5):
        fetch_size = top_k * 5  
        docs = self.vectorstore.similarity_search(query, k=fetch_size)

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

        formatted = "\n".join(
            f"{idx+1}. {song['Artist']} – {song['Title']} ({song['Year']})"
            for idx, song in enumerate(results)
        )

        return f"Here are {len(results)} songs I recommend based on your mood:\n{formatted}"

    def run_query(self, query: str):
        return self.chain({"question": query})
    


# Automatically load dataset when module is imported
DATASET_PATH = os.path.join("datasets", "music.json")
music_data = load_music_dataset(DATASET_PATH)
rag_chain = MusicRAGChain(music_data, model_name=DEFAULT_MODEL_NAME)
