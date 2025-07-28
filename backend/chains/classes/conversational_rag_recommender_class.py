import json
import logging
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from app.core.memory_store import get_memory
from app.services.downloader import download_song_list
from app.core.config import DEFAULT_MODEL_NAME

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open("prompts/suggest_songs_rag.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()


class ConversationalRagRecommender:
    def __init__(self, rag_chain, model_name: str = DEFAULT_MODEL_NAME):
        # Always use ChatOllama (works for both chat and text models)
        self.llm = ChatOllama(model=model_name)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        self.chain = RunnableWithMessageHistory(
            self.prompt | self.llm,
            get_session_history=get_memory,
            input_messages_key="input",
            history_messages_key="history"
        )
        self.song_memory = {}
        self.session_playlists = {}
        self.rag_chain = rag_chain

    def _extract_content(self, response):
        """Ensure compatibility with both chat messages and raw strings."""
        return response.content if hasattr(response, "content") else str(response)

    def detect_intent(self, message: str) -> str:
        prompt = f"""
Classify the user's intent into one of these categories:
- recommendation
- modify_playlist
- download
- other

User message: "{message}"
Respond with only one word: recommendation, modify_playlist, download, or other.
"""
        response = self.llm.invoke(prompt)
        return self._extract_content(response).strip().lower()

    def extract_constraints(self, message: str, current_playlist=None) -> dict:
        playlist_text = ""
        if current_playlist:
            playlist_text = "\n".join(f"{s['artist']} – {s['title']}" for s in current_playlist)
        prompt = f"""
You are analyzing a request to modify a music playlist. 
Here is the current playlist:
{playlist_text}

User message: "{message}"

Extract and return strict JSON:
{{
  "exclude_artists": [],
  "exclude_decades": [],
  "exclude_genres": [],
  "exclude_moods": []
}}
"""
        response = self.llm.invoke(prompt)
        try:
            return json.loads(self._extract_content(response))
        except json.JSONDecodeError:
            return {"exclude_artists": [], "exclude_decades": [], "exclude_genres": [], "exclude_moods": []}

    def convert_rag_to_struct(self, rag_result: str) -> list:
        structured = []
        for line in rag_result.splitlines():
            if " – " in line:
                try:
                    _, rest = line.split(". ", 1)
                    artist, title_decade = rest.split(" – ", 1)
                    title, decade = title_decade.rsplit("(", 1)
                    structured.append({
                        "artist": artist.strip(),
                        "title": title.strip(),
                        "decade": decade.replace(")", "").strip(),
                        "genre": "unknown",
                        "mood": "unknown"
                    })
                except ValueError:
                    continue
        return structured

    def modify_playlist(self, session_id: str, constraints: dict) -> list:
        playlist = self.session_playlists.get(session_id, [])
        filtered = [
            s for s in playlist
            if s["artist"] not in constraints["exclude_artists"]
            and s["decade"] not in constraints["exclude_decades"]
            and s["genre"] not in constraints["exclude_genres"]
            and s["mood"] not in constraints["exclude_moods"]
        ]
        needed = max(0, 10 - len(filtered))
        if needed > 0:
            query_parts = []
            if constraints["exclude_artists"]:
                query_parts.append("excluding artists: " + ", ".join(constraints["exclude_artists"]))
            if constraints["exclude_decades"]:
                query_parts.append("excluding decades: " + ", ".join(constraints["exclude_decades"]))
            if constraints["exclude_genres"]:
                query_parts.append("excluding genres: " + ", ".join(constraints["exclude_genres"]))
            if constraints["exclude_moods"]:
                query_parts.append("excluding moods: " + ", ".join(constraints["exclude_moods"]))
            query = "motivational songs " + " ".join(query_parts)
            new_songs = self.convert_rag_to_struct(self.rag_chain.recommend_songs(query, top_k=needed))
            filtered.extend(new_songs)
        self.session_playlists[session_id] = filtered
        return filtered

    def format_playlist(self, playlist: list) -> str:
        return "\n".join(f"{i+1}. {s['artist']} – {s['title']} ({s['decade']})" for i, s in enumerate(playlist))

    def ask(self, user_message: str, session_id: str = "default") -> str:
        intent = self.detect_intent(user_message)
        if intent == "recommendation":
            rag_result = self.rag_chain.recommend_songs(user_message, top_k=10)
            playlist = self.convert_rag_to_struct(rag_result)
            self.session_playlists[session_id] = playlist
            self.song_memory[session_id] = [f"{s['artist']} – {s['title']}" for s in playlist]
            return self.format_playlist(playlist)
        if intent == "modify_playlist":
            if session_id not in self.session_playlists:
                return "⚠️ No playlist to modify yet."
            constraints = self.extract_constraints(user_message, self.session_playlists[session_id])
            updated_playlist = self.modify_playlist(session_id, constraints)
            self.song_memory[session_id] = [f"{s['artist']} – {s['title']}" for s in updated_playlist]
            return self.format_playlist(updated_playlist)
        if intent == "download":
            songs = self.song_memory.get(session_id)
            if not songs:
                return "⚠️ No songs to download for this session."
            paths = download_song_list(songs, session_id=session_id)
            return "✅ Downloaded songs:\n" + "\n".join(paths)
        # fallback to generic chat
        response = self.rag_chain.chat(user_message)
        return response if isinstance(response, str) else self._extract_content(response)
