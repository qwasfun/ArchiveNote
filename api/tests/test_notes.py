"""
笔记（Notes）接口测试：增删改查、搜索、分页。
"""

import pytest


@pytest.mark.asyncio
async def test_create_note(client, auth_headers):
    """创建笔记成功。"""
    response = await client.post(
        "/api/v1/notes/",
        json={"title": "Test Note", "content": "Hello world"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Hello world"
    assert data["visibility"] == "PRIVATE"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_note_unauthenticated(client):
    """未认证创建笔记应返回 401。"""
    response = await client.post(
        "/api/v1/notes/",
        json={"title": "Anon Note", "content": "content"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_notes_empty(client, auth_headers):
    """新用户笔记列表为空。"""
    response = await client.get("/api/v1/notes/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_list_notes_pagination(client, auth_headers):
    """笔记列表支持分页。"""
    for i in range(5):
        await client.post(
            "/api/v1/notes/",
            json={"title": f"Note {i}", "content": f"Content {i}"},
            headers=auth_headers,
        )

    response = await client.get(
        "/api/v1/notes/", params={"page": 1, "page_size": 3}, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_list_notes_search(client, auth_headers):
    """全文搜索笔记。"""
    await client.post(
        "/api/v1/notes/",
        json={"title": "Python Tutorial", "content": "Learn Python"},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/notes/",
        json={"title": "Go Tutorial", "content": "Learn Go"},
        headers=auth_headers,
    )

    response = await client.get(
        "/api/v1/notes/", params={"q": "Python"}, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Python Tutorial"


@pytest.mark.asyncio
async def test_get_note(client, auth_headers):
    """通过 ID 获取笔记详情。"""
    create_resp = await client.post(
        "/api/v1/notes/",
        json={"title": "Detail Note", "content": "Detail content"},
        headers=auth_headers,
    )
    note_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == note_id


@pytest.mark.asyncio
async def test_get_note_not_found(client, auth_headers):
    """获取不存在的笔记应返回 404。"""
    response = await client.get("/api/v1/notes/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_note(client, auth_headers):
    """更新笔记标题和内容。"""
    create_resp = await client.post(
        "/api/v1/notes/",
        json={"title": "Old Title", "content": "Old content"},
        headers=auth_headers,
    )
    note_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/notes/{note_id}",
        json={"title": "New Title", "content": "New content"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["content"] == "New content"


@pytest.mark.asyncio
async def test_delete_note(client, auth_headers):
    """删除笔记后无法再获取。"""
    create_resp = await client.post(
        "/api/v1/notes/",
        json={"title": "To Delete", "content": "bye"},
        headers=auth_headers,
    )
    note_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    get_resp = await client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_note_isolation_between_users(client):
    """不同用户之间的笔记相互隔离。"""
    # 用户 A
    resp_a = await client.post(
        "/api/v1/auth/register",
        data={"username": "user_a", "password": "pw_a"},
    )
    headers_a = {"Authorization": f"Bearer {resp_a.json()['access_token']}"}
    await client.post(
        "/api/v1/notes/",
        json={"title": "A's Note", "content": "private"},
        headers=headers_a,
    )

    # 用户 B
    resp_b = await client.post(
        "/api/v1/auth/register",
        data={"username": "user_b", "password": "pw_b"},
    )
    headers_b = {"Authorization": f"Bearer {resp_b.json()['access_token']}"}

    list_resp = await client.get("/api/v1/notes/", headers=headers_b)
    assert list_resp.json()["total"] == 0
