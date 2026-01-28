#!/bin/bash

echo "🚀 Starting Zeabur deployment script..."
echo "📂 Current directory: $(pwd)"
echo "👤 User: $(whoami)"

# Force stdout/stderr flushing
export PYTHONUNBUFFERED=1

# 1. Start FastAPI backend (Background)
echo "🔧 Starting FastAPI backend..."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info &
FASTAPI_PID=$!
echo "🆔 FastAPI PID: $FASTAPI_PID"

# Wait loop to ensure FastAPI is up
echo "⏳ Waiting for FastAPI to accept connections..."
for i in {1..10}; do
    if python -c "import socket; s = socket.socket(); s.connect(('127.0.0.1', 8000)); s.close()" 2>/dev/null; then
        echo "✅ FastAPI is running!"
        break
    fi
    
    # Check if process died
    if ! kill -0 $FASTAPI_PID 2>/dev/null; then
        echo "❌ FastAPI process died unexpectedly!"
        exit 1
    fi
    
    sleep 2
done

# 2. Start Streamlit frontend (Foreground)
PORT=${PORT:-8080}
echo "🎨 Starting Streamlit frontend on port $PORT..."

# Note: server.address=0.0.0.0 allows external access
# server.headless=true is mandatory for cloud environments
python -m streamlit run coach_app.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false

# Exit handler
echo "🛑 Streamlit exited. Killing FastAPI..."
kill $FASTAPI_PID
