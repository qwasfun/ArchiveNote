"""
认证接口测试：注册、登录、获取当前用户、刷新 Token。
"""

import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    """首次注册成功，自动成为系统管理员并创建默认 Workspace。"""
    response = await client.post(
        "/api/v1/auth/register",
        data={"username": "alice", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "alice"
    # 第一个注册用户自动成为系统管理员
    assert data["user"]["is_system_admin"] is True


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    """重复用户名注册应返回 400。"""
    await client.post(
        "/api/v1/auth/register",
        data={"username": "bob", "password": "password123"},
    )
    response = await client.post(
        "/api/v1/auth/register",
        data={"username": "bob", "password": "other_password"},
    )
    assert response.status_code == 400
    assert "已经存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_second_user_not_admin(client):
    """第二个注册用户不是系统管理员。"""
    await client.post(
        "/api/v1/auth/register",
        data={"username": "first", "password": "password123"},
    )
    response = await client.post(
        "/api/v1/auth/register",
        data={"username": "second", "password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["user"]["is_system_admin"] is False


@pytest.mark.asyncio
async def test_login_success(client):
    """使用正确凭据登录成功。"""
    await client.post(
        "/api/v1/auth/register",
        data={"username": "carol", "password": "mypassword"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "carol", "password": "mypassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "carol"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """密码错误应返回 401。"""
    await client.post(
        "/api/v1/auth/register",
        data={"username": "dave", "password": "correct_pw"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "dave", "password": "wrong_pw"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """不存在的用户登录应返回 401。"""
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "nobody", "password": "pw"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client, auth_headers):
    """持有有效 token 可获取当前用户信息。"""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "is_system_admin" in data


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client):
    """未认证请求应返回 401。"""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client):
    """使用 refresh_token cookie 换取新的 access_token。"""
    login_resp = await client.post(
        "/api/v1/auth/register",
        data={"username": "eve", "password": "password123"},
    )
    assert login_resp.status_code == 200
    # httpx 会自动保存 set-cookie，再次请求时携带
    refresh_resp = await client.post("/api/v1/auth/refresh")
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()


@pytest.mark.asyncio
async def test_check_is_system_admin(client, auth_headers):
    """检查当前用户是否为系统管理员接口。"""
    response = await client.get("/api/v1/auth/is-system-admin", headers=auth_headers)
    assert response.status_code == 200
    assert "is_system_admin" in response.json()
