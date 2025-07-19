# 🎵 Mood-Based Music Recommendation Chatbot (LangChain + Ollama + FastAPI)

This project is an intelligent music chatbot that asks how you're feeling and automatically recommends 10 songs that match your mood using a local LLM (**Gemma via Ollama**). With a single click, it also downloads the suggested songs from YouTube as `.wav` files.

## ✨ Features

- 🤖 LLM-powered mood understanding using **Gemma 3B/4B** (via Ollama)
- 🎶 Prompt-based song recommendations with LangChain
- 📥 Automatic song downloading using `yt_dlp`
- 🚀 Built with FastAPI and ready for integration with a frontend
- 📂 Clean modular structure for chains, tools, and prompts
- 🔍 Interactive testing via Swagger (`/docs`)

## 📦 Tech Stack

- **LangChain** (modern Runnable interface)
- **LangChain-Ollama** for local LLM calls
- **Ollama** to run Gemma models locally
- **FastAPI** backend
- **yt_dlp** for high-quality audio download
- **Python 3.10+**

## 📁 Folder Structure

```
music_chatbot/
├── main.py                    # FastAPI app
├── chains/
│   └── mood_to_songs_chain.py
├── tools/
│   └── download_tool.py
├── prompts/
│   └── suggest_songs.txt
├── downloads/                # Output folder
└── requirements.txt
```

## 🚀 How It Works

1. You send a mood like `"nostalgic"` to the `/mood-to-download` endpoint.
2. The chatbot uses **Gemma** to suggest 10 songs that match your mood.
3. The songs are automatically downloaded from YouTube as `.wav` files.

## 🛠️ Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install langchain-ollama

# 2. Start Ollama (make sure gemma is downloaded)
ollama run gemma3:4b

# 3. Run FastAPI
uvicorn main:app --reload

# 4. Visit Swagger UI
http://localhost:8000/docs
```

---

Enjoy your personalized music experience! 🎧
