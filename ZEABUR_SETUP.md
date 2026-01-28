# Zeabur PostgreSQL 設定指引

本文件說明如何在 Zeabur 上設定 PostgreSQL 資料庫並連結到 DEXsystem 應用。

## 步驟 1: 建立 PostgreSQL 服務

1. 進入你的 Zeabur 專案頁面
2. 點擊 **「Create Service」** 或 **「新增服務」**
3. 選擇 **「Prebuilt」** → **「PostgreSQL」**
4. 等待 PostgreSQL 服務建立完成(通常 1-2 分鐘)

## 步驟 2: 連結環境變數

### 方法 A: 自動連結(推薦)

1. 在 PostgreSQL 服務頁面,找到 **「Connections」** 或 **「連線」** 區塊
2. 點擊你的應用服務名稱(例如 `dexsystem`)
3. Zeabur 會自動將 `DATABASE_URL` 環境變數注入到你的應用

### 方法 B: 手動設定

如果自動連結沒有生效:

1. 在 PostgreSQL 服務頁面,複製 **「Connection String」** 或 **「DATABASE_URL」**
   - 格式: `postgresql://username:password@host:port/database`
2. 進入你的應用服務設定
3. 找到 **「Environment Variables」** 或 **「環境變數」**
4. 新增變數:
   - **Key**: `DATABASE_URL`
   - **Value**: 貼上剛才複製的連線字串

## 步驟 3: 重新部署應用

1. 修改任何檔案(例如在 `README.md` 加個空行)並 push 到 Git
2. 或在 Zeabur 應用服務頁面點擊 **「Redeploy」**
3. 等待部署完成

## 步驟 4: 驗證資料庫連線

### 檢查部署日誌

1. 進入應用服務頁面
2. 查看 **「Logs」** 或 **「日誌」**
3. 確認沒有資料庫連線錯誤
4. 應該會看到類似訊息:
   ```
   INFO:     Started server process
   INFO:     Uvicorn running on http://0.0.0.0:8080
   ```

### 測試應用功能

開啟你的應用網址,測試以下功能:

- ✅ 新增教練
- ✅ 新增課程  
- ✅ 紀錄上課
- ✅ 紀錄賣課
- ✅ 查看老闆頁面統計資料

## 步驟 5: 查看資料庫內容

### 使用 Zeabur 內建工具

1. 進入 PostgreSQL 服務頁面
2. 點擊 **「Console」** 或 **「控制台」**
3. 執行 SQL 查詢:
   ```sql
   -- 查看所有資料表
   \dt
   
   -- 查看教練資料
   SELECT * FROM teachers;
   
   -- 查看上課紀錄
   SELECT * FROM attendances;
   ```

### 使用外部工具(pgAdmin, DBeaver 等)

1. 在 PostgreSQL 服務頁面找到連線資訊:
   - Host
   - Port
   - Database
   - Username
   - Password
2. 使用這些資訊在本地工具中建立連線

## 常見問題

### Q: 部署後出現 "could not connect to server" 錯誤

**A:** 檢查環境變數 `DATABASE_URL` 是否正確設定:
1. 進入應用服務 → Environment Variables
2. 確認 `DATABASE_URL` 存在且格式正確
3. 重新部署

### Q: 資料表沒有自動建立

**A:** 確認 `migrate_db.py` 有被執行:
1. 檢查 `start_zeabur.sh` 是否包含 `python migrate_db.py`
2. 查看部署日誌確認執行結果
3. 如果沒有,可以手動在 Zeabur Console 執行:
   ```bash
   python migrate_db.py
   ```

### Q: 如何遷移現有的 SQLite 資料?

**A:** 如果本地 `dexsystem.db` 有重要資料:
1. 使用 `sqlite3` 匯出資料為 SQL:
   ```bash
   sqlite3 dexsystem.db .dump > backup.sql
   ```
2. 修改 SQL 檔案以相容 PostgreSQL 語法
3. 使用 `psql` 匯入到 Zeabur PostgreSQL:
   ```bash
   psql $DATABASE_URL < backup.sql
   ```

### Q: 本地開發如何使用 PostgreSQL?

**A:** 有兩個選擇:
1. **繼續使用 SQLite**(推薦): 不設定 `DATABASE_URL` 環境變數,程式會自動使用 SQLite
2. **使用本地 PostgreSQL**: 
   ```bash
   # 安裝 PostgreSQL
   brew install postgresql
   
   # 建立資料庫
   createdb dexsystem_dev
   
   # 設定環境變數
   export DATABASE_URL="postgresql://localhost/dexsystem_dev"
   
   # 初始化資料庫
   python migrate_db.py
   ```

## 支援

如有問題,請參考:
- [Zeabur PostgreSQL 文件](https://zeabur.com/docs/marketplace/postgresql)
- [SQLAlchemy 文件](https://docs.sqlalchemy.org/)
