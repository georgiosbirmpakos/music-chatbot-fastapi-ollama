
# 🎵 Music Chatbot

An AI-powered conversational music assistant that suggests songs based on your mood and downloads them as `.wav` files using YouTube.

---

## 🧠 Chat with the Bot & Download Songs

You can interact with the chatbot via `/chat` and receive 10 song suggestions based on your prompt. Once you're happy with the list, simply confirm and the songs will be downloaded automatically.

---

### 1. 🎤 Start a Chat

Send a POST request to `/chat`:

```http
POST /chat
Content-Type: application/json

{
  "message": "I feel nostalgic",
  "session_id": "anna"
}
```

---

### 2. 🧾 Adjust Recommendations (Optional)

Refine your playlist by chatting:

```json
{
  "message": "Add some classic rock",
  "session_id": "anna"
}
```

---

### 3. ✅ Confirm to Download

Once ready, trigger the download:

```json
{
  "message": "Yes, download them",
  "session_id": "anna"
}
```

Response:
```json
{
  "reply": "Great! I've started downloading your list. Saved to: downloads/"
}
```

---

## 🧑‍💻 Developer Setup Guide

### ✅ Prerequisites

- Python 3.10+
- FFmpeg (for audio conversion)
- Git
- Conda or `venv` (optional, recommended)

---

### 🔧 Installation

```bash
git clone https://github.com/georgiosbirmpakos/music-chatbot-fastapi-ollama.git
cd music_chatbot
pip install -r requirements.txt
```

Ensure `ffmpeg` is installed and in your PATH.

---

### 🚀 Run the Server

```bash
uvicorn main:app --reload
```

Open Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 🧠 Models & Memory

- Uses `LangChain` and `Ollama` (e.g., `gemma3:4b`) for chat
- Tracks user context using `InMemoryChatMessageHistory`
- Prompts loaded from `prompts/suggest_songs.txt`

---

### 📦 Folder Structure

```
.
├── app
│   ├── api              # FastAPI route definitions
│   ├── core             # Session memory handling
│   └── services         # Downloader logic
├── chains               # LangChain logic & orchestration
├── prompts              # Initial prompt template
├── downloads            # Where .wav files are saved
├── main.py              # FastAPI app entrypoint
├── requirements.txt
└── README.md
```

---

### 🔩 Extend the Bot

- To add new tools (e.g., genre filtering), extend `chains/conversational_recommender.py`
- To support other formats (.mp3), modify `tools/youtube_downloader.py`
- To persist memory across sessions, replace `InMemoryChatMessageHistory` with Redis or another store

---


