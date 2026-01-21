from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# 同步引擎（用于数据库迁移和枚举缓存刷新）
sync_engine = create_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# 异步引擎（用于应用层异步操作）
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False
)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


def get_db():
    """同步数据库会话（用于数据库迁移）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """异步数据库会话（用于应用层操作）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# 刷新枚举类型缓存
def refresh_enum_cache():
    """刷新 PostgreSQL 枚举类型缓存"""
    try:
        with sync_engine.connect() as conn:
            # 强制刷新枚举类型
            conn.execute(text("SELECT NULL::interviewstatus"))
            conn.commit()
    except Exception as e:
        print(f"刷新枚举缓存时出错: {e}")


# 在模块加载时刷新枚举缓存
refresh_enum_cache()