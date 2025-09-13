from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class Recording:
    mbid: str
    title: str

    # OPTIONALS below
    genre: Optional[str] = None
    artist: Optional[str] = None
    first_release_date: Optional[str] = None
    decade: Optional[int] = None
    duration_ms: Optional[int] = None

    def to_json(self) -> Dict[str, Any]:
        return asdict(self)