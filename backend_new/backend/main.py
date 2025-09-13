# backend/main.py
from typing import List, Optional
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.classes import MusicBrainzClient,RecordingQuery
from backend.dto.RecordingDTO import RecordingDTO, NLQueryIn
from backend.helpers import get_mb_client, get_openai_client, nl_to_query_and_limit  
from contextlib import asynccontextmanager
from openai import OpenAI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # init singletons once per process
    app.state.mb_client = MusicBrainzClient()
    app.state.openai_client = OpenAI()  # reads OPENAI_API_KEY from env
    yield
    # optional: teardown logic

app = FastAPI(title="MusicBrainz Wrapper API", version="0.1.0", lifespan=lifespan)

# Simple CORS for local dev; tighten for prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ---- Dependency: singleton MB client
def get_mb_client() -> MusicBrainzClient:
    # Create once and reuse (musicbrainzngs already rate-limits)
    if not hasattr(app.state, "mb_client"):
        app.state.mb_client = MusicBrainzClient()
    return app.state.mb_client

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


@app.post("/search/recordings", response_model=List[RecordingDTO], tags=["search"])
def search_recordings(
    body: Optional[RecordingQuery] = None,          # <- dataclass, optional
    limit: int = Query(20, ge=1, le=100),
    enrich_missing_dates: bool = Query(True),
    enrich_genres: bool = Query(True),
    mbc: MusicBrainzClient = Depends(get_mb_client),
):
    """
    Send any subset of fields; empty body does a wildcard search (*).
    """
    q = body or RecordingQuery()                    # <- use what was provided, or an empty query

    try:
        results = mbc.search_recordings(
            query=q,
            limit=limit,
            enrich_missing_dates=enrich_missing_dates,
            enrich_genres=enrich_genres,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

    return [
        RecordingDTO(
            mbid=r.mbid,
            title=r.title,
            genre=r.genre,
            artist=r.artist,
            first_release_date=r.first_release_date,
            decade=r.decade,
            duration_ms=r.duration_ms,
        )
        for r in results
    ]

@app.post("/nl/search/recordings", response_model=List[RecordingDTO], tags=["search"])
def search_recordings_nl(
    body: NLQueryIn,
    limit: int = Query(20, ge=1, le=100),
    enrich_missing_dates: bool = Query(True),
    enrich_genres: bool = Query(True),
    mbc = Depends(get_mb_client),
    openai_client: OpenAI = Depends(get_openai_client),
):
    try:
        q, nl_limit = nl_to_query_and_limit(body.query)
        effective_limit = nl_limit or limit
        # clamp for safety
        if effective_limit < 1: effective_limit = 1
        if effective_limit > 100: effective_limit = 100

        results = mbc.search_recordings(
            query=q,
            limit=effective_limit,
            enrich_missing_dates=enrich_missing_dates,
            enrich_genres=enrich_genres,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"NL parse or upstream error: {e}")

    return [
        RecordingDTO(
            mbid=r.mbid, title=r.title, genre=r.genre, artist=r.artist,
            first_release_date=r.first_release_date, decade=r.decade,
            duration_ms=r.duration_ms
        )
        for r in results
    ]