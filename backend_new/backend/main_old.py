# backend/main.py
from typing import List, Optional
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.classes import MusicBrainzClient,RecordingQuery
from backend.dto.RecordingDTO import RecordingDTO, NLQueryIn
from backend.helpers import get_mb_client, get_openai_client, nl_to_query_and_limit  
from contextlib import asynccontextmanager
from openai import OpenAI
from typing import Literal
from pydantic import BaseModel, ConfigDict
from backend.tools.intention import IntentionClassifier
from backend.tools import YouTubeDownloader, DownloadListInput, DownloadResult
from backend.tools import make_nl_parser_tool

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
    if not hasattr(app.state, "mb_client"):
        app.state.mb_client = MusicBrainzClient()
    return app.state.mb_client

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


@app.post("/search/recordings", response_model=List[RecordingDTO], tags=["search"])
def search_recordings(
    body: Optional[RecordingQuery] = None,          
    limit: int = Query(20, ge=1, le=100),
    enrich_missing_dates: bool = Query(True),
    enrich_genres: bool = Query(True),
    mbc: MusicBrainzClient = Depends(get_mb_client),
):
    """
    Send any subset of fields; empty body does a wildcard search (*).
    """
    q = body or RecordingQuery()                    

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

class IntentionIn(BaseModel):
    query: str
    model_config = ConfigDict(json_schema_extra={
        "examples": [{"query": "10 hard rock songs from the 80s between 3 and 5 minutes"}]
    })

class IntentionOut(BaseModel):
    intention: Literal["generic","suggestion","modification"]
    reason: str

# Singleton-ish instance (or build via lifespan/app.state if you prefer)
_intention = IntentionClassifier()

@app.post("/nl/intention", response_model=IntentionOut, tags=["nl"])
def detect_intention(body: IntentionIn):
    res = _intention.classify(body.query)
    return IntentionOut(intention=res.intention, reason=res.reason)

yd = YouTubeDownloader()

@app.post("/tools/youtube/download", response_model=list[DownloadResult], tags=["tools"])
def youtube_download(body: DownloadListInput):
    return [r.dict() for r in yd.download_batch(body.songs, max_songs=body.max_songs)]


class NLParseIn(BaseModel):
    query: str
    model_config = ConfigDict(json_schema_extra={
        "examples": [{"query": "10 hard rock songs from the 80s between 3 and 5 minutes"}]
    })

class NLParseOut(BaseModel):
    artist: Optional[str] = None
    title: Optional[str] = None
    genre: Optional[str] = None
    isrc: Optional[str] = None
    min_duration_ms: Optional[int] = None
    max_duration_ms: Optional[int] = None
    decade: Optional[int] = None
    extra_terms: List[str] = []
    limit: Optional[int] = None

nl_parser_tool = make_nl_parser_tool()    

@app.post("/nl/parse-and-search", response_model=List[RecordingDTO], tags=["nl"])
def nl_parse_and_search(
    body: NLParseIn,
    limit: int = Query(20, ge=1, le=100),
    enrich_missing_dates: bool = Query(True),
    enrich_genres: bool = Query(True),
    mbc = Depends(get_mb_client),
):
    parsed: dict = nl_parser_tool.invoke({"query": body.query})  # uses your nl tool
    q = RecordingQuery(
        artist=parsed.get("artist"),
        title=parsed.get("title"),
        genre=parsed.get("genre"),
        isrc=parsed.get("isrc"),
        min_duration_ms=parsed.get("min_duration_ms"),
        max_duration_ms=parsed.get("max_duration_ms"),
        decade=parsed.get("decade"),
        extra_terms=parsed.get("extra_terms") or [],
    )
    eff_limit = parsed.get("limit") or limit
    eff_limit = max(1, min(100, eff_limit))  # clamp

    try:
        results = mbc.search_recordings(
            query=q,
            limit=eff_limit,
            enrich_missing_dates=enrich_missing_dates,
            enrich_genres=enrich_genres,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

    return [
        RecordingDTO(
            mbid=r.mbid, title=r.title, genre=r.genre, artist=r.artist,
            first_release_date=r.first_release_date, decade=r.decade,
            duration_ms=r.duration_ms
        ) for r in results
    ]