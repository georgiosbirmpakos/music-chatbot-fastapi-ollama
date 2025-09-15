# backend/agent/builder.py
from __future__ import annotations
from pathlib import Path
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import render_text_description

# NEW: message history wrapper + store
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from backend.state.memory import LatestListStore
from backend.classes import MusicBrainzClient
from backend.tools.suggest_songs import make_suggest_songs_tool
from backend.tools.modify_list import make_modify_latest_tool
from backend.tools.download_latest import make_download_latest_tool

# simple in-process history store (per-session)
_histories: Dict[str, InMemoryChatMessageHistory] = {}

def _get_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _histories:
        _histories[session_id] = InMemoryChatMessageHistory()
    return _histories[session_id]

def build_agent(
    mbc: MusicBrainzClient,
    store: LatestListStore,
    model: str,
    session_id: str,
):
    system_template = Path(__file__).resolve().parents[1] / "prompts" / "agent_system.txt"
    system_text = system_template.read_text(encoding="utf-8")

    llm = ChatOpenAI(model=model, temperature=0)

    tools = [
        make_suggest_songs_tool(mbc, store),
        make_modify_latest_tool(mbc, store),
        make_download_latest_tool(store),
    ]

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            system_text
            + "\n\nYou have access to these tools:\n{tools}\n"
              "Only call tools using these exact names: {tool_names}."
        ),
        # IMPORTANT: include chat history in the prompt
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        # REQUIRED for tool-calling agent
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    tool_text = render_text_description(tools)
    tool_names = ", ".join(t.name for t in tools)

    # bind static vars
    prompt = prompt.partial(
        session_id=session_id,   # fills {session_id} in your system prompt
        tools=tool_text,
        tool_names=tool_names,
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    # Wrap with message history
    runnable = RunnableWithMessageHistory(
        executor,
        get_session_history=_get_history,        # function(session_id) -> InMemoryChatMessageHistory
        input_messages_key="input",              # where user text comes in
        history_messages_key="chat_history",     # the placeholder you added above
        output_messages_key="output",            # where final text is written
    )
    return runnable
