from langchain_core.chat_history import InMemoryChatMessageHistory

_sessions = {}

def get_memory(session_id: str):
    if session_id not in _sessions:
        _sessions[session_id] = InMemoryChatMessageHistory()
    return _sessions[session_id]
