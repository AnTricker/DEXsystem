#!/bin/bash

# DEXsystem 啟動腳本
# 用途: 同時啟動 FastAPI backend 和 Streamlit frontend,支援手機訪問

echo "🚀 正在啟動 DEXsystem..."
echo ""

# 取得本機 IP
IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1)
echo "📱 你的區域網路 IP: $IP"
echo ""

# 啟動 FastAPI (背景執行)
echo "🔧 啟動 FastAPI backend (port 8000)..."
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
FASTAPI_PID=$!

# 等待 FastAPI 啟動
sleep 2

# 啟動 Streamlit (前景執行)
echo "🎨 啟動 Streamlit frontend (port 8501)..."
echo ""
echo "================================"
echo "✅ 服務已啟動!"
echo "================================"
echo "📱 手機訪問網址: http://$IP:8501"
echo "💻 電腦訪問網址: http://localhost:8501"
echo ""
echo "按 Ctrl+C 停止服務"
echo "================================"
echo ""

streamlit run coach_app.py --server.address 0.0.0.0 --server.port 8501

# 當 Streamlit 停止時,也停止 FastAPI
kill $FASTAPI_PID
