#!/bin/bash

# 啟動 FastAPI backend (背景執行)
# 綁定到 localhost，因為只需要讓同容器內的 Streamlit 訪問
echo "🔧 Starting FastAPI backend..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
FASTAPI_PID=$!

# 等待後端啟動
sleep 3

# 啟動 Streamlit frontend
# Zeabur 會注入 PORT 環境變數，預設使用 8080
PORT=${PORT:-8080}
echo "🎨 Starting Streamlit frontend on port $PORT..."

# 設定 server.address 為 0.0.0.0 以接受外部請求
streamlit run coach_app.py --server.port $PORT --server.address 0.0.0.0

# 當 Streamlit 停止時，也停止 FastAPI
kill $FASTAPI_PID
