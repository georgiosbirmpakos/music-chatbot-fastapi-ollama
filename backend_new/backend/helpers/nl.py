# backend/helpers/nl.py
import json
import re
from typing import Optional, Tuple
from backend.classes import RecordingQuery
from .config import get_openai_client, OPENAI_MODEL

SCHEMA_TEXT = """
Return ONLY valid JSON (no prose) for:
{
  "artist": string|null,
  "title": string|null,
  "genre": string|null,                // maps to MusicBrainz tag:
  "isrc": string|null,
  "min_duration_ms": integer|null,     // >= 0
  "max_duration_ms": integer|null,     // >= 0
  "decade": integer|null,              // e.g., 1990 for the 90s
  "extra_terms": string[],             // default []
  "limit": integer|null                // desired number of results, 1..100
}
Rules:
- "90s" => decade=1990; "80s" => 1980, etc.
- Convert durations like "3-5 minutes", "under 4 min", "210 seconds" to ms.
- If unknown, use null (or [] for extra_terms).
- If the user mentions a count like "10 songs", set limit to that number (1..100).
- Do not invent ISRCs.
"""

_JSON_RE = re.compile(r"\{.*\}", re.S)
_INT_RE  = re.compile(r"\b(\d{1,3})\b")

def _extract_json(text: str) -> dict:
    m = _JSON_RE.search(text or "")
    if not m:
        raise ValueError("No JSON found in model output.")
    return json.loads(m.group(0))

def _heuristic_limit(nl: str) -> Optional[int]:
    # Grab the first reasonable integer 1..100 if present (e.g., "10 songs", "top 25")
    m = _INT_RE.search(nl or "")
    if not m:
        return None
    try:
        val = int(m.group(1))
        if 1 <= val <= 100:
            return val
    except Exception:
        pass
    return None

def nl_to_query_and_limit(nl: str) -> Tuple[RecordingQuery, Optional[int]]:
    client = get_openai_client()
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SCHEMA_TEXT},
            {"role": "user", "content": nl},
        ],
    )
    content = resp.choices[0].message.content
    data = _extract_json(content)

    extra_terms = data.get("extra_terms") or []
    limit = data.get("limit")
    if limit is None:
        limit = _heuristic_limit(nl)

    q = RecordingQuery(
        artist=data.get("artist"),
        title=data.get("title"),
        genre=data.get("genre"),
        isrc=data.get("isrc"),
        min_duration_ms=data.get("min_duration_ms"),
        max_duration_ms=data.get("max_duration_ms"),
        decade=data.get("decade"),
        extra_terms=extra_terms,
    )
    return q, (int(limit) if isinstance(limit, int) else None)
