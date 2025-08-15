# Music Agent Chatbot

## Overview
This project is a mood-based **music recommendation chatbot** that suggests songs, modifies playlists via natural language, and downloads tracks from YouTube. It integrates a React frontend with a FastAPI backend powered by LangChain, Ollama, and FAISS.

---

## Features
- **Chat-based interaction** for music discovery.
- **Mood-based song recommendations** using a curated dataset.
- **Playlist modification** (add, remove, replace, reorder) via natural language.
- **YouTube audio download** as MP3 with metadata tagging.
- **Session-based conversation memory** for personalized recommendations.

---

## Architecture
**Frontend**: React + Tailwind CSS  
**Backend**: FastAPI + LangChain + HuggingFace + FAISS  
**LLM Runtime**: Ollama (`mistral:7b` by default)  
**Downloader**: yt_dlp + FFmpeg  
**Data Storage**: JSON datasets for curated songs (mood, genre, decade)

### Flow
1. User sends message from frontend → Backend `/chat-conversational-rag`.
2. Backend detects intent: recommend / modify playlist / download / other.
3. Recommendations: Query FAISS (MiniLM embeddings) → LLM → return results.
4. Playlist ops: Apply structured modifications to in-memory playlist.
5. Download: Fetch MP3 via `yt_dlp` and save to `~/Downloads`.

---

## Folder Structure
```
backend/
  main.py
  app/
    core/
    api/
    services/
  chains/
  datasets/
  prompts/
  tools/
frontend/
  src/
  public/
start_infra.sh
requirements.txt
```

---

## Key Technologies
- **FastAPI** – REST API framework for backend
- **LangChain** – Orchestrates LLM-based RAG
- **Ollama** – Local LLM runtime
- **FAISS** – In-memory vector search
- **HuggingFace Transformers** – Sentence embeddings (`all-MiniLM-L6-v2`)
- **yt_dlp** – YouTube download
- **React + Tailwind CSS** – Frontend UI

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama installed locally (`https://ollama.ai`)
- FFmpeg installed for audio processing

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start
```

---

## Running with Script
You can use `start_infra.sh` to start Ollama, backend, and frontend in sequence.  
Make sure to adjust the model in `start_infra.sh` to your preference (`mistral:7b`, `tinyllama:1.1b`, etc.).

---

## Example API Request
```json
POST /chat-conversational-rag
{
  "message": "I'm feeling happy today, suggest some songs",
  "session_id": "user123"
}
```

