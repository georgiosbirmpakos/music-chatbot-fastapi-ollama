# backend/app/core/song_index.py

import os
import json

def load_music_dataset(dataset_path: str):
    """
    Loads your music dataset.
    Expected format: JSON array with 'title', 'artist', 'mood', 'lyrics', etc.
    Example:
    [
        {"title": "Song A", "artist": "Artist 1", "mood": "happy", "lyrics": "..."},
        {"title": "Song B", "artist": "Artist 2", "mood": "sad", "lyrics": "..."}
    ]
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        songs = json.load(f)

    # Convert songs into simple text for embeddings
    music_texts = []
    for song in songs:
        text = f"Title: {song.get('title','')} | Artist: {song.get('artist','')} | Mood: {song.get('mood','')} | Lyrics: {song.get('lyrics','')}"
        music_texts.append(text)

    return music_texts
