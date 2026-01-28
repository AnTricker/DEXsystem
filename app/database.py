from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite 資料庫設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./dexsystem.db"

# 建立資料庫引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite 需要此設定
)

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
