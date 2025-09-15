# backend/tools/download_latest.py
from __future__ import annotations
from typing import Dict
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from backend.state.memory import LatestListStore
from backend.tools.youtube_downloader import YouTubeDownloader, SongItem

class DownloadLatestInput(BaseModel):
    session_id: str = Field(..., description="Conversation session id")

def make_download_latest_tool(
    store: LatestListStore,
    downloader: YouTubeDownloader | None = None
) -> StructuredTool:
    yd = downloader or YouTubeDownloader()

    def _impl(**kwargs) -> Dict:
        inp = DownloadLatestInput(**kwargs)
        latest = store.get(inp.session_id)
        if not latest:
            return {"results": [], "note": "No latest list to download. Ask for suggestions first."}

        items = [SongItem(title=it.get("title",""), artist=it.get("artist")) for it in latest]
        results = yd.download_batch(items)
        return {"results": [r.dict() for r in results]}

    return StructuredTool.from_function(
        name="download_latest_playlist",
        description="Download the latest suggested list to MP3 in the user's Downloads folder. Always include session_id.",
        func=_impl,
        args_schema=DownloadLatestInput,
        return_direct=False,
    )
