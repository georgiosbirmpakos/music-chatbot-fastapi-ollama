from langchain.llms import Ollama
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from app.core.config import DEFAULT_MODEL_NAME
import os
import json


def load_music_dataset(dataset_path: str):
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    with open(dataset_path, "r", encoding="utf-8") as f:
        songs = json.load(f)
    return [
        f"Title: {song['title']} | Artist: {song['artist']} | Mood: {song['mood']} | "
        f"Genre: {song['genre']} | Year: {song['year']} | Lyrics: {song['lyrics']}"
        for song in songs
    ]


class MusicRAGChain:
    def __init__(self, music_data: list[str], model_name: str = DEFAULT_MODEL_NAME):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = FAISS.from_documents([Document(page_content=text) for text in music_data], self.embeddings)
        self.llm = Ollama(model=model_name)

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
        return "\n".join(f"{i+1}. {s['Artist']} – {s['Title']} ({s['Year']})" for i, s in enumerate(results))

    # For general conversation, bypass retrieval entirely
    def chat(self, message: str):
        return self.llm(message)


# Auto-load dataset
DATASET_PATH = os.path.join("datasets", "music.json")
music_data = load_music_dataset(DATASET_PATH)
rag_chain = MusicRAGChain(music_data, model_name=DEFAULT_MODEL_NAME)
