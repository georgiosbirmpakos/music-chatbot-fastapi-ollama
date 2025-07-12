from fastapi import FastAPI
from pydantic import BaseModel
from chains.mood_to_songs_chain import get_mood_to_songs_chain
from tools.download_tool import download_song_from_youtube
import re

app = FastAPI()
chain = get_mood_to_songs_chain()

class MoodRequest(BaseModel):
    mood: str

class DownloadRequest(BaseModel):
    songs: list[str]

@app.post("/recommend")
def recommend_songs(request: MoodRequest):
    try:
        result = chain.invoke({"mood": request.mood})

        # Debug: Show entire LLM output
        print("\n🧠 Raw LLM result:", result)

        # If result is an object with .content (ChatMessage), use that
        content = result.content if hasattr(result, "content") else str(result)

        print("\n🎵 Parsed content:\n", content)

        songs = [line.strip("0123456789. ") for line in content.splitlines() if line.strip()]
        return {"mood": request.mood, "songs": songs[:10]}
    
    except Exception as e:
        print(f"\n❌ Error in recommend_songs: {e}")
        return {"error": str(e)}


@app.post("/download")
def download_songs(request: DownloadRequest):
    responses = [download_song_from_youtube(song) for song in request.songs]
    return {"download_status": responses}

@app.post("/mood-to-download")
def mood_to_download(request: MoodRequest):
    try:
        # Step 1: Get song suggestions from the LLM
        result = chain.invoke({"mood": request.mood})

        # Step 2: Extract the main text field
        content = result.get("text") if isinstance(result, dict) else (
            result.content if hasattr(result, "content") else str(result)
        )

        print("\n🎵 Cleaned LLM Text:\n", content)

        # Step 3: Parse only numbered song lines (1. ..., 2. ..., etc.)
        lines = content.splitlines()
        numbered_lines = [line for line in lines if re.match(r"^\s*\d+[\.\-]", line)]

        if numbered_lines:
            songs = [
                re.sub(r'^\s*\d+[\.\-]?\s*[“”"\'-]*', '', line).strip()
                for line in numbered_lines
            ]
        else:
            songs = []

        # Step 4: Handle case where no valid songs are found
        if not songs:
            return {
                "mood": request.mood,
                "suggested_songs": [],
                "download_status": [],
                "error": "No valid song suggestions found in the LLM response."
            }

        # Step 5: Download each suggested song
        responses = [download_song_from_youtube(song) for song in songs[:10]]

        return {
            "mood": request.mood,
            "suggested_songs": songs[:10],
            "download_status": responses
        }

    except Exception as e:
        print(f"\n❌ Error in mood_to_download: {e}")
        return {"error": str(e)}


