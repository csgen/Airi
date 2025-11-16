from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os

DB_URL = os.getenv('APP_DATABASE_ASYNC_URL')

engine = create_async_engine(
    DB_URL,
    echo=True,   # 开发阶段方便调试
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)