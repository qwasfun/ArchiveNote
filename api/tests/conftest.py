"""
pytest 测试配置与共享 fixtures。

重要：环境变量必须在导入任何 app 模块之前设置，
因为 database.py 和 jwt.py 在模块加载时就读取环境变量。
"""

import os
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio

# ─── 在导入 app 模块前设置必要的环境变量 ───────────────────────────
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/archivenote_test",
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("SECRET_KEY", "test-secret-key-do-not-use-in-production")
# ───────────────────────────────────────────────────────────────────

from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.app import app  # noqa: E402
from app.database import Base, get_async_session  # noqa: E402


# 替换 app lifespan，跳过测试中的数据库迁移
@asynccontextmanager
async def _noop_lifespan(app):
    yield


app.router.lifespan_context = _noop_lifespan


# ─── Session 级别 fixtures（整个测试会话只创建一次表）────────────────


@pytest_asyncio.fixture(scope="session")
async def engine():
    """创建测试引擎，建立所有表；测试结束后清除。"""
    _engine = create_async_engine(TEST_DATABASE_URL)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


# ─── Function 级别 fixtures（每个测试函数独立）──────────────────────


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db(engine):
    """每个测试结束后清空所有表数据，保证测试隔离。"""
    yield
    async with engine.begin() as conn:
        # reversed(sorted_tables) 保证先删子表再删父表
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def db_session(engine):
    """每个测试提供独立的数据库 session。"""
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """提供注入测试 session 的 HTTPX 异步客户端。"""

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def registered_user(client):
    """注册一个测试用户并返回注册响应（含 access_token）。"""
    response = await client.post(
        "/api/v1/auth/register",
        data={"username": "testuser", "password": "testpassword123"},
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest_asyncio.fixture
async def auth_headers(registered_user):
    """返回测试用户的 Bearer 认证头。"""
    return {"Authorization": f"Bearer {registered_user['access_token']}"}
