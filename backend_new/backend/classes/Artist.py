from dataclasses import dataclass
from typing import Optional

@dataclass
class Artist:
    mbid: str
    name: str
    sort_name: Optional[str] = None