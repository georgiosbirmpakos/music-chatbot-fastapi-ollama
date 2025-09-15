# backend/tools/suggest_songs.py
from __future__ import annotations
from typing import Optional, List, Callable, Dict
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from backend.classes import MusicBrainzClient, RecordingQuery
from backend.helpers.nl import nl_to_query_and_limit
from backend.state.memory import LatestListStore

CAP = 20  # hard cap per requirements

class SuggestInput(BaseModel):
    session_id: str = Field(..., description="Conversation session id")
    # Natural language OR structured fields (both allowed; NL wins if provided)
    nl_query: Optional[str] = Field(None, description="Natural language prompt for songs")
    artist: Optional[str] = None
    title: Optional[str] = None
    genre: Optional[str] = None
    isrc: Optional[str] = None
    min_duration_ms: Optional[int] = None
    max_duration_ms: Optional[int] = None
    decade: Optional[int] = None
    extra_terms: List[str] = Field(default_factory=list)
    limit: Optional[int] = Field(default=20, ge=1, le=100)

def make_suggest_songs_tool(
    mbc: MusicBrainzClient,
    store: LatestListStore,
) -> StructuredTool:
    def _impl(**kwargs) -> Dict:
        inp = SuggestInput(**kwargs)
        # resolve limit with hard cap=20
        req_limit = inp.limit or CAP
        eff_limit = min(req_limit, CAP)
        capped = req_limit > CAP

        # Build RecordingQuery
        if inp.nl_query:
            q, parsed_limit = nl_to_query_and_limit(inp.nl_query)
            if parsed_limit:
                eff_limit = min(parsed_limit, CAP)
        else:
            q = RecordingQuery(
                artist=inp.artist, title=inp.title, genre=inp.genre, isrc=inp.isrc,
                min_duration_ms=inp.min_duration_ms, max_duration_ms=inp.max_duration_ms,
                decade=inp.decade, extra_terms=inp.extra_terms
            )

        results = mbc.search_recordings(
            query=q, limit=eff_limit,
            enrich_missing_dates=True, enrich_genres=True
        )
        # shape for memory + return
        songs = [{
            "mbid": r.mbid,
            "title": r.title,
            "artist": r.artist,
            "genre": r.genre,
            "duration_ms": r.duration_ms,
            "first_release_date": r.first_release_date,
            "decade": r.decade,
        } for r in results]

        store.set(inp.session_id, songs)
        note = "You have reached the limit of 20 songs." if capped else None
        return {"songs": songs, "count": len(songs), "capped": capped, "note": note}

    return StructuredTool.from_function(
        name="suggest_songs",
        description=(
            "Suggest up to 20 songs using MusicBrainz. "
            "Accepts natural language (nl_query) or structured filters. "
            "Always include session_id."
        ),
        func=_impl,
        args_schema=SuggestInput,
        return_direct=False,
    )
