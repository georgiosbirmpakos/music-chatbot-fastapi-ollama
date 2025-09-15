# backend/agent/agent.py
from typing import Optional
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.classes import MusicBrainzClient
from backend.helpers import get_mb_client 
from contextlib import asynccontextmanager
from openai import OpenAI
from pydantic import BaseModel, ConfigDict
import os, uuid
from pydantic import BaseModel, ConfigDict
from backend.state.memory import LatestListStore
from backend.agent.builder import build_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mb_client = MusicBrainzClient()
    app.state.openai_client = OpenAI()
    app.state.latest_store = LatestListStore()
    yield    


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

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Dependency to get store
def get_store() -> LatestListStore:
    return app.state.latest_store

class AgentIn(BaseModel):
    query: str
    session_id: Optional[str] = None
    model_config = ConfigDict(json_schema_extra={
        "examples":[{"query":"10 hard rock songs from the 80s between 3 and 5 minutes","session_id":"demo-user-1"}]
    })

class AgentOut(BaseModel):
    response: str

@app.post("/agent/chat", response_model=AgentOut, tags=["agent"])
def agent_chat(
    body: AgentIn,
    mbc = Depends(get_mb_client),
    store: LatestListStore = Depends(get_store),
):
    session_id = body.session_id or f"anon-{uuid.uuid4().hex[:8]}"
    agent = build_agent(mbc=mbc, store=store, model=OPENAI_MODEL, session_id=session_id)

    result = agent.invoke(
        {"input": body.query},
        config={"configurable": {"session_id": session_id}},
    )
    return AgentOut(response=result.get("output", ""))

