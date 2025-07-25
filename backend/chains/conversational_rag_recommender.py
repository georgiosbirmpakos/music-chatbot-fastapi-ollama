import os
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from app.core.memory_store import get_memory
from app.services.downloader import download_song_list
from app.core.config import DEFAULT_MODEL_NAME
from chains.music_rag_chain import rag_chain

# Load dynamic prompt from file
with open("prompts/suggest_songs_rag.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()


class ConversationalRagRecommender:
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        # Use Ollama LLM for natural conversation
        self.llm = ChatOllama(model=model_name)

        # Build the conversation template
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

    def ask(self, user_message: str, session_id: str = "default") -> str:
        # Trigger RAG only when explicitly asking for suggestions
        if any(word in user_message.lower() for word in ["suggest", "recommend"]):
            rag_result = rag_chain.recommend_songs(user_message, top_k=10)
            self.song_memory[session_id] = [
                line.split(". ", 1)[-1]
                for line in rag_result.splitlines()
                if line.strip().startswith(tuple("1234567890")) and " – " in line
            ]
            return rag_result

        # Download confirmation
        if user_message.lower() in ["yes", "sure", "ok", "fine", "go ahead", "download", "yep"]:
            songs = self.song_memory.get(session_id)
            if not songs:
                return "⚠️ I don’t have any song list to download for this session yet."
            paths = download_song_list(songs, session_id=session_id)
            return "✅ Downloaded songs:\n" + "\n".join(paths)

        # Default conversational response
        response = rag_chain.chat(user_message)
        return response if isinstance(response, str) else str(response)


    def download_stored_songs(self, session_id: str) -> list[str]:
        songs = self.song_memory.get(session_id)
        if not songs:
            return ["⚠️ No songs stored for this session."]
        return download_song_list(songs, session_id=session_id)
