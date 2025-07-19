from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from app.services.downloader import download_song_list
from app.core.memory_store import get_memory

# Load dynamic system prompt
with open("prompts/suggest_songs.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Template with memory
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

class ConversationalRecommender:
    def __init__(self, model_name: str = "gemma3:4b"):
        self.llm = ChatOllama(model=model_name)
        self.chain = RunnableWithMessageHistory(
            prompt | self.llm,
            get_session_history=get_memory,
            input_messages_key="input",
            history_messages_key="history"
        )
        self.song_memory = {}

    def ask(self, user_message: str, session_id: str = "default") -> str:
        response = self.chain.invoke(
            {"input": user_message},
            config={"configurable": {"session_id": session_id}}
        )

        reply = response.content if hasattr(response, "content") else str(response)

        # ✅ Store songs only if they look like a list (e.g. 1. Artist - Title)
        song_lines = [
            line.strip().split(". ", 1)[-1]
            for line in reply.splitlines()
            if line.strip().startswith(tuple("1234567890")) and " - " in line
        ]

        if song_lines:
            self.song_memory[session_id] = song_lines

        # ✅ Trigger download if user agrees
        if user_message.lower() in ["yes", "sure", "ok", "fine", "go ahead", "download", "yep"]:
            songs = self.song_memory.get(session_id)
            if not songs:
                return "⚠️ I don’t have any song list to download for this session yet."
            paths = download_song_list(songs, session_id=session_id)
            return f"✅ Downloaded songs:\n" + "\n".join(paths)

        return reply

    def download_stored_songs(self, session_id: str) -> list[str]:
        songs = self.song_memory.get(session_id)
        if not songs:
            return ["⚠️ No songs stored for this session."]
        return download_song_list(songs, session_id=session_id)
