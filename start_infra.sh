#!/bin/bash

set -e

echo "🚀 Starting Music Chatbot Infrastructure..."

# 1. Activate conda environment
echo "🔹 Activating conda environment: music-chatbot"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate music-chatbot

# 2. Start Ollama (Mistral 7B)
echo "🔹 Starting Ollama with mistral:7b"
ollama run mistral:7b &
OLLAMA_PID=$!
sleep 5  # give it some time to warm up

# 3. Start Backend
echo "🔹 Starting FastAPI backend"
cd backend
uvicorn main:app --reload &
BACKEND_PID=$!
cd ..

# 4. Wait until backend is ready
echo "⏳ Waiting for backend to be ready..."
until curl --output /dev/null --silent --head --fail http://localhost:8000/docs; do
    printf '.'
    sleep 10
done
echo -e "\n✅ Backend is up!"

# 5. Start Frontend
echo "🔹 Starting React frontend"
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Handle shutdown cleanly
trap "echo 'Shutting down...'; kill $OLLAMA_PID $BACKEND_PID $FRONTEND_PID" EXIT

wait
