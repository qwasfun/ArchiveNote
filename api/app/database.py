import uuid
from datetime import datetime

from sqlalchemy import Column, String, UUID, Text, DateTime
from sqlalchemy.orm import declarative_base

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# 使用异步 sqlite 驱动 aiosqlite
DATABASE_URL = "sqlite+aiosqlite:///./data/app.sqlite"
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
