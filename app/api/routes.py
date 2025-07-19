from fastapi import APIRouter
from pydantic import BaseModel

from chains.mood_to_songs_chain import MoodToSongsChain
from tools.youtube_downloader import YouTubeDownloader
from app.services.music_service import MusicService

router = APIRouter()

class MoodRequest(BaseModel):
    text: str

# Instantiate dependencies
chain = MoodToSongsChain()
downloader = YouTubeDownloader()
service = MusicService(chain, downloader)

@router.post("/mood-to-download")
def mood_to_download(mood: MoodRequest):
    return service.recommend_and_download(mood.text)
