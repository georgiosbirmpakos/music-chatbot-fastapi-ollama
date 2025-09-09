#!/bin/bash
set -euo pipefail

# always run from repo root
cd "$(dirname "$0")"

echo "🔹 Activating conda env: music-chatbot"
# try common conda.sh locations
if [ -f "$(conda info --base 2>/dev/null)/etc/profile.d/conda.sh" ]; then
  source "$(conda info --base)/etc/profile.d/conda.sh"
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
  source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
  source "$HOME/anaconda3/etc/profile.d/conda.sh"
else
  echo "❌ conda.sh not found"; exit 1
fi
conda activate music-chatbot

trap 'echo "🧹 Stopping..."; kill 0 || true' EXIT

echo "🔹 Starting FastAPI backend"
cd backend
# --reload can misbehave on Windows background; start stable first
python -m uvicorn main:app --host 127.0.0.1 --port 8000 & 
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend..."
# hit a simple JSON endpoint with GET
until curl -fsS http://127.0.0.1:8000/diag/health >/dev/null; do
  printf '.'
  sleep 20
done
echo -e "\n✅ Backend is up!"

echo "🔹 Starting React frontend"
cd frontend
npm start &
FRONTEND_PID=$!
cd -

echo "💤 PIDs: backend=$BACKEND_PID frontend=$FRONTEND_PID (Ctrl+C to stop)"
wait
