from langchain_core.tools import StructuredTool
from pydantic import BaseModel
from backend.helpers.nl import nl_to_query_and_limit

class NLParserInput(BaseModel):
    query: str

def make_nl_parser_tool() -> StructuredTool:
    def _impl(query: str) -> dict:
        q, limit = nl_to_query_and_limit(query)
        return {
            "artist": q.artist, "title": q.title, "genre": q.genre, "isrc": q.isrc,
            "min_duration_ms": q.min_duration_ms, "max_duration_ms": q.max_duration_ms,
            "decade": q.decade, "extra_terms": q.extra_terms, "limit": limit,
        }
    return StructuredTool.from_function(
        name="nl_parser",
        description="Parse natural language into a structured RecordingQuery + optional limit.",
        func=_impl,
        args_schema=NLParserInput,
        return_direct=False,
    )
