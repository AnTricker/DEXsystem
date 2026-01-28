# DEXsystem - 舞蹈教室數位化管理系統

## 專案簡介
**DEXsystem** 是一個專為舞蹈教室設計的現代化管理解決方案。本專案結合了高效能的 **FastAPI** 後端與使用者友善的 **Streamlit** 前端介面，專注於解決舞蹈教室日常營運中的痛點：教練上課紀錄、銷售業績追蹤以及自動薪資計算。

系統採用 **Mobile First** 設計，確保教練能隨時隨地透過手機輕鬆操作，同時為管理者提供功能強大的數據儀表板。

## 主要功能

### 📱 教練端 (Coach App)
- **上課紀錄**: 快速填寫上課資訊（日期、課程、人數），系統自動依據人數級距計算當堂薪資。
- **銷售紀錄**: 直覺化的賣課介面，支援多種方案組合與自訂金額，自動計算銷售提成。
- **手機優化**: 專為行動裝置打造的 UI/UX，包含大按鈕設計與九宮格數字鍵盤，提升操作體驗。

### 👑 管理端 (Boss Dashboard)
- **財務儀表板**: 即時檢視月度總收入、總支出與淨利，掌握營運狀況。
- **薪資規則設定**: 可動態調整「上課人數 vs 薪資」的級距規則，設定後立即生效並應用於後續計算。
- **數據中心**: 完整的上課與銷售紀錄查詢功能，支援 Excel (CSV) 匯出以便進行進階分析。
- **自動化月結**: 系統自動彙整教練每月的基本薪資與銷售提成，產出薪資統計表。

## 技術架構

- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: Streamlit, Pandas
- **Database**: SQLite (本地開發) / PostgreSQL (生產環境)
- **Environment**: 支援 Docker 或 Python Virtual Environment 部署
- **Deployment**: Zeabur (詳見 [ZEABUR_SETUP.md](ZEABUR_SETUP.md))

## 快速開始

### 1. 環境需求
確認您的系統已安裝此版本或更高的 Python：
- Python 3.10+

### 2. 安裝步驟

Clone 專案到本地：
```bash
git clone <your-repo-url>
cd DEXsystem
```

建立並啟動虛擬環境：
```bash
# Mac / Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

安裝依賴套件：
```bash
pip install -r requirements.txt
```

設定環境變數（可省略，預設使用 Localhost）：
```bash
cp .env.example .env
```

### 3. 啟動服務

我們提供了一個便捷的腳本來同時啟動後端 API 與前端介面：

```bash
chmod +x start_server.sh
./start_server.sh
```

服務啟動後，您將看到以下資訊：
- **手機訪問網址**: `http://<您的區域網路IP>:8501` (需在同一 Wi-Fi 下)
- **電腦訪問網址**: `http://localhost:8501`
- **API 文件**: `http://localhost:8000/docs`

## 專案結構

```
DEXsystem/
├── app/                  # FastAPI 後端核心程式碼
│   ├── main.py           # 應用程式入口與 API路由
│   ├── models.py         # 資料庫模型定義 (SQLAlchemy)
│   ├── schemas.py        # 資料驗證模型 (Pydantic)
│   ├── crud.py           # 資料庫 CRUD 操作
│   ├── database.py       # 資料庫連線設定
│   └── salary_rules.py   # 薪資計算邏輯模組
├── coach_app.py          # Streamlit 前端應用程式
├── start_server.sh       # 系統啟動腳本
├── requirements.txt      # Python 相依套件清單
├── salary_rules.json     # 薪資規則設定檔 (由系統自動維護)
├── dexsystem.db          # SQLite 資料庫檔案
├── .env.example          # 環境變數範例
└── README.md             # 專案說明文件
```

## 開發者指南

- **資料庫管理**: 本專案使用 SQLite，可使用 DB Browser for SQLite 等工具開啟 `dexsystem.db` 進行查看。
- **前端樣式**: 主要樣式定義於 `coach_app.py` 中的 `apply_custom_style()` 函數，採用 CSS Injection 方式客製化 Streamlit 介面。
- **API 擴充**: 後端遵循 RESTful 風格，若需新增功能請於 `app/main.py` 註冊新的 Router 並實作對應的 CRUD。

---
Created by Antigravity
