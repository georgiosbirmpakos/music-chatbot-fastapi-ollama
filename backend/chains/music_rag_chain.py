from langchain.llms import Ollama
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from app.core.config import DEFAULT_MODEL_NAME
import os
import json
import glob

def load_all_music_datasets(dataset_folder: str):
    """Load all JSON datasets from the folder and merge them."""
    all_songs = []
    json_files = glob.glob(os.path.join(dataset_folder, "*.json"))
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            songs = json.load(f)
            for song in songs:
                all_songs.append(
                    f"Title: {song['title']} | Artist: {song['artist']} | Mood: {song['mood']} | "
                    f"Genre: {song['genre']} | Decade: {song['decade']}"
                )
    return all_songs

class MusicRAGChain:
    def __init__(self, music_data: list[str], model_name: str = DEFAULT_MODEL_NAME):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = FAISS.from_documents(
            [Document(page_content=text) for text in music_data], self.embeddings
        )
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
        return "\n".join(f"{i+1}. {s['Artist']} – {s['Title']} ({s['Decade']})" for i, s in enumerate(results))

    def chat(self, message: str):
        return self.llm(message)

# Auto-load all datasets
DATASET_FOLDER = os.path.join("datasets")
music_data = load_all_music_datasets(DATASET_FOLDER)
rag_chain = MusicRAGChain(music_data, model_name=DEFAULT_MODEL_NAME)
