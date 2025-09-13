from pydantic import  BaseModel, Field
from typing import Optional

class RecordingDTO(BaseModel):
    mbid: str
    title: str
    genre: Optional[str] = None
    artist: Optional[str] = None
    first_release_date: Optional[str] = None
    decade: Optional[int] = None
    duration_ms: Optional[int] = Field(default=None, ge=0)

class NLQueryIn(BaseModel):
    query: str    