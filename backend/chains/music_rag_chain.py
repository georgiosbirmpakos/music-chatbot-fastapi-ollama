import os, json, glob
from chains.classes.music_rag_chain_class import MusicRAGChain
from app.core.config import DEFAULT_MODEL_NAME

def load_all_music_datasets(dataset_folder: str):
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

DATASET_FOLDER = os.path.join("datasets")
music_data = load_all_music_datasets(DATASET_FOLDER)
rag_chain = MusicRAGChain(music_data, model_name=DEFAULT_MODEL_NAME)
