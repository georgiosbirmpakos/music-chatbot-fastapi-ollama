# backend/tools/youtube_downloader.py
from __future__ import annotations
import os
import re
from pathlib import Path
from typing import List, Optional, Literal

import yt_dlp
from pydantic import BaseModel, Field, validator
from langchain_core.tools import StructuredTool


# ---------- Pydantic schemas for tool I/O ----------

class SongItem(BaseModel):
    title: str = Field(..., description="Song title, e.g., Billie Jean")
    artist: Optional[str] = Field(None, description="Artist name, e.g., Michael Jackson")

    def as_query(self) -> str:
        return f"{self.artist} - {self.title}" if self.artist else self.title


class DownloadListInput(BaseModel):
    songs: List[SongItem] = Field(..., description="List of songs to download as MP3")
    # Optional cap; keep consistent with your product rules. Default None -> no cap here.
    max_songs: Optional[int] = Field(
        default=None,
        ge=1,
        description="Optional cap; if provided, only the first N songs are processed."
    )

    @validator("songs")
    def non_empty(cls, v):
        if not v:
            raise ValueError("songs must not be empty")
        return v


class DownloadResult(BaseModel):
    query: str
    path: Optional[str] = None
    status: Literal["ok", "skipped", "error"]
    error: Optional[str] = None


# ---------- Concrete implementation (your template + batch) ----------

class YouTubeDownloader:
    def __init__(self):
        self.download_folder = Path.home() / "Downloads"
        self.download_folder.mkdir(exist_ok=True)

    def sanitize_filename(self, name: str) -> str:
        """
        Removes illegal characters for Windows and replaces them with underscores.
        Also replaces en-dash with a normal hyphen.
        """
        safe_name = re.sub(r'[<>:"/\\|?*]', "_", name)
        return safe_name.replace("–", "-")

    def download(self, song_name: str) -> str:
        """
        Search YouTube for the song and download the best audio as .mp3.
        Returns the path to the downloaded file.
        """
        safe_name = self.sanitize_filename(song_name)
        output_template = os.path.join(self.download_folder, f"{safe_name}.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "default_search": "ytsearch1",
            "outtmpl": output_template,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_name, download=True)
            filename = ydl.prepare_filename(info)
            final_filename = os.path.splitext(filename)[0] + ".mp3"
            return final_filename

    def download_batch(self, items: List[SongItem], max_songs: Optional[int] = None) -> List[DownloadResult]:
        """
        Sequentially download a list of songs. Returns per-item results.
        """
        if max_songs is not None:
            items = items[:max_songs]

        results: List[DownloadResult] = []
        for it in items:
            q = it.as_query()
            try:
                path = self.download(q)
                results.append(DownloadResult(query=q, path=path, status="ok"))
            except Exception as e:
                results.append(DownloadResult(query=q, status="error", error=str(e)))
        return results


# ---------- LangChain Structured Tool factory ----------

def make_youtube_download_tool(downloader: Optional[YouTubeDownloader] = None) -> StructuredTool:
    """
    Returns a LangChain StructuredTool named 'youtube_downloader'.
    Input schema:
      {
        "songs": [{"title": "...", "artist": "...?"}, ...],
        "max_songs": 20   // optional
      }
    Output: list of {query, path, status, error}
    """
    yd = downloader or YouTubeDownloader()

    def _impl(songs: List[SongItem], max_songs: Optional[int] = None) -> List[dict]:
        results = yd.download_batch(songs, max_songs=max_songs)
        # Return plain dicts (LC likes JSON-serializable returns)
        return [r.dict() for r in results]

    tool = StructuredTool.from_function(
        name="youtube_downloader",
        description=(
            "Download a list of songs from YouTube as MP3 into the user's Downloads folder. "
            "Each song is an object with title and optional artist. "
            "Use max_songs to cap the number processed."
        ),
        func=_impl,
        args_schema=DownloadListInput,
        return_direct=False,
    )
    return tool
