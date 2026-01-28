# 使用官方 Python 輕量版映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
# 防止 Python 產生 .pyc 檔案
ENV PYTHONDONTWRITEBYTECODE=1
# 防止 Python 緩衝輸出 (讓 log 即時顯示)
ENV PYTHONUNBUFFERED=1

# 安裝系統依賴 (如果有些套件需要編譯，可能需要 build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有專案檔案
COPY . .

# 確保啟動腳本有執行權限
RUN chmod +x start_zeabur.sh

# 宣告埠號 (Zeabur 會自動注入 PORT，這裡僅作宣告)
EXPOSE 8080

# 啟動命令
CMD ["bash", "start_zeabur.sh"]
