# backend/tools/modify_list.py
from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from backend.state.memory import LatestListStore
from backend.helpers.nl import nl_to_query_and_limit
from backend.classes import MusicBrainzClient

CAP = 20

class ModifyInput(BaseModel):
    session_id: str = Field(..., description="Conversation session id")
    remove_by_index: Optional[List[int]] = Field(default=None, description="0-based indices to remove")
    remove_by_title: Optional[List[str]] = Field(default=None, description='Titles to remove (case-insensitive match)')
    # Refill settings:
    refill_nl_query: Optional[str] = Field(default=None, description="Constraints for replacements (NL)")
    refill_to: Optional[int] = Field(default=CAP, ge=1, le=CAP, description="Target size after refill (max 20)")

def make_modify_latest_tool(
    mbc: MusicBrainzClient,
    store: LatestListStore,
) -> StructuredTool:
    def _impl(**kwargs) -> Dict:
        inp = ModifyInput(**kwargs)
        current = store.get(inp.session_id)
        if not current:
            return {"songs": [], "count": 0, "note": "No latest list to modify. Ask for suggestions first."}

        # Remove by index
        to_remove_idx = set(inp.remove_by_index or [])
        keep = [item for i, item in enumerate(current) if i not in to_remove_idx]

        # Remove by title (case-insensitive)
        rm_titles = {t.strip().lower() for t in (inp.remove_by_title or []) if t and t.strip()}
        if rm_titles:
            keep = [it for it in keep if it.get("title","").lower() not in rm_titles]

        # Refill
        target = max(1, min(inp.refill_to or CAP, CAP))
        need = max(0, target - len(keep))

        if need > 0 and inp.refill_nl_query:
            q, parsed_limit = nl_to_query_and_limit(inp.refill_nl_query)
            # We refill only what we need (<= CAP)
            results = mbc.search_recordings(
                query=q, limit=need, enrich_missing_dates=True, enrich_genres=True
            )
            additions = [{
                "mbid": r.mbid,
                "title": r.title,
                "artist": r.artist,
                "genre": r.genre,
                "duration_ms": r.duration_ms,
                "first_release_date": r.first_release_date,
                "decade": r.decade,
            } for r in results]
            # Deduplicate by (title, artist)
            seen = {(it["title"], it.get("artist")) for it in keep}
            for a in additions:
                key = (a["title"], a.get("artist"))
                if key not in seen and len(keep) < target:
                    keep.append(a); seen.add(key)

        store.set(inp.session_id, keep)
        return {"songs": keep, "count": len(keep)}

    return StructuredTool.from_function(
        name="modify_latest_list",
        description=(
            "Modify the latest suggested list by removing items and optionally refilling with new suggestions. "
            "Always include session_id."
        ),
        func=_impl,
        args_schema=ModifyInput,
        return_direct=False,
    )
