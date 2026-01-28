from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# 優先使用環境變數的 DATABASE_URL (Zeabur PostgreSQL)
# 本地開發則使用 SQLite
SQLALCHEMY_DATABASE_URL = config('DATABASE_URL', default='sqlite:///./dexsystem.db')

# 根據資料庫類型設定不同的 connect_args
if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
    # SQLite 需要 check_same_thread
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL 不需要 check_same_thread
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 建立 Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 宣告 Base 類別
Base = declarative_base()

# 取得資料庫 session 的依賴函數
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
