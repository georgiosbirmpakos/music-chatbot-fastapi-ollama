from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RecordingQuery:
    artist: Optional[str] = None
    title: Optional[str] = None
    genre: Optional[str] = None
    isrc: Optional[str] = None
    min_duration_ms: Optional[int] = None
    max_duration_ms: Optional[int] = None
    decade: Optional[int] = None 
    extra_terms: List[str] = field(default_factory=list)

    def to_lucene(self) -> str:
        def q(text: str) -> str:
            return text.replace('"', r'\"')

        parts: List[str] = []
        if self.artist:
            parts.append(f'artist:"{q(self.artist)}"')
        if self.title:
            parts.append(f'recording:"{q(self.title)}"')
        if self.genre:
            parts.append(f'tag:"{q(self.genre)}"')
        if self.isrc:
            parts.append(f'isrc:{self.isrc}')
        if self.min_duration_ms is not None or self.max_duration_ms is not None:
            min_val = self.min_duration_ms if self.min_duration_ms is not None else "*"
            max_val = self.max_duration_ms if self.max_duration_ms is not None else "*"
            parts.append(f'dur:[{min_val} TO {max_val}]')
        if self.decade is not None:
            start = f"{int(self.decade)}-01-01"
            end = f"{int(self.decade) + 9}-12-31"
            parts.append(f'firstreleasedate:[{start} TO {end}]')
        parts.extend(self.extra_terms)
        return " AND ".join(parts) if parts else "*"