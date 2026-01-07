from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 刷新枚举类型缓存
def refresh_enum_cache():
    """刷新 PostgreSQL 枚举类型缓存"""
    try:
        with engine.connect() as conn:
            # 强制刷新枚举类型
            conn.execute(text("SELECT NULL::interviewstatus"))
            conn.commit()
    except Exception as e:
        print(f"刷新枚举缓存时出错: {e}")


# 在模块加载时刷新枚举缓存
refresh_enum_cache()