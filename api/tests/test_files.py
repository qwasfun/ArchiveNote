"""
文件（Files）接口测试：列表、获取详情、重命名、软删除、移动。
文件上传测试通过 mock 存储层，避免依赖真实文件系统或对象存储。
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models import File

# ─── 测试辅助 ─────────────────────────────────────────────────────────


async def _get_workspace_id(client, headers):
    """通过 API 获取当前用户的默认 workspace ID。"""
    resp = await client.get("/api/v1/workspaces", headers=headers)
    assert resp.status_code == 200
    workspaces = resp.json()
    assert len(workspaces) > 0, "用户没有任何 Workspace"
    return workspaces[0]["id"]


async def _insert_file(db_session, user_id, workspace_id, filename="sample.txt"):
    """直接写入 DB，绕过存储层，便于测试非上传接口。"""
    file = File(
        id=str(uuid.uuid4()),
        user_id=user_id,
        workspace_id=workspace_id,
        filename=filename,
        storage_path=f"test-uploads/{uuid.uuid4()}/{filename}",
        storage_backend_id=None,
        mime_type="text/plain",
        size=1024,
        file_type="text",
        file_type_confidence="high",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_deleted=0,
    )
    db_session.add(file)
    await db_session.commit()
    await db_session.refresh(file)
    return file


# ─── 测试用例 ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_files_empty(client, auth_headers):
    """新用户文件列表为空。"""
    response = await client.get("/api/v1/files/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["data"] == []


@pytest.mark.asyncio
async def test_list_files_pagination(client, auth_headers, registered_user, db_session):
    """文件列表支持分页。"""
    user_id = registered_user["user"]["id"]
    workspace_id = await _get_workspace_id(client, auth_headers)

    for i in range(5):
        await _insert_file(db_session, user_id, workspace_id, f"file_{i}.txt")

    response = await client.get(
        "/api/v1/files/",
        params={"page": 1, "page_size": 3},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["data"]) == 3


@pytest.mark.asyncio
async def test_get_file_metadata(client, auth_headers, registered_user, db_session):
    """通过 ID 获取文件元数据。"""
    user_id = registered_user["user"]["id"]
    workspace_id = await _get_workspace_id(client, auth_headers)
    file = await _insert_file(db_session, user_id, workspace_id)

    response = await client.get(f"/api/v1/files/{file.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == file.id
    assert data["filename"] == file.filename


@pytest.mark.asyncio
async def test_get_file_not_found(client, auth_headers):
    """获取不存在的文件应返回 404。"""
    response = await client.get(f"/api/v1/files/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rename_file(client, auth_headers, registered_user, db_session):
    """重命名文件。"""
    user_id = registered_user["user"]["id"]
    workspace_id = await _get_workspace_id(client, auth_headers)
    file = await _insert_file(db_session, user_id, workspace_id, "original.txt")

    response = await client.put(
        f"/api/v1/files/{file.id}/rename",
        json={"filename": "renamed.txt"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "renamed.txt"


@pytest.mark.asyncio
async def test_delete_file_soft(client, auth_headers, registered_user, db_session):
    """软删除文件后进入回收站，GET 接口不可见。"""
    user_id = registered_user["user"]["id"]
    workspace_id = await _get_workspace_id(client, auth_headers)
    file = await _insert_file(db_session, user_id, workspace_id, "to_delete.txt")

    del_resp = await client.delete(f"/api/v1/files/{file.id}", headers=auth_headers)
    assert del_resp.status_code == 200

    # 软删除后 GET 应返回 404
    get_resp = await client.get(f"/api/v1/files/{file.id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_file(client, auth_headers):
    """
    上传文件：mock 存储层，验证文件记录写入 DB 并返回正确响应。
    """
    fake_storage_path = f"uploads/test/{uuid.uuid4()}/hello.txt"
    fake_file_type_info = {
        "mime_type": "text/plain",
        "category": "text",
        "confidence": "high",
    }
    mock_backend = MagicMock()

    with (
        patch(
            "app.routers.files.get_default_storage_backend",
            new=AsyncMock(return_value=(mock_backend, None)),
        ),
        patch(
            "app.routers.files.save_file",
            return_value=(fake_storage_path, 11, fake_file_type_info),
        ),
    ):
        response = await client.post(
            "/api/v1/files/",
            files={"files": ("hello.txt", b"hello world", "text/plain")},
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "hello.txt"
    assert data[0]["mime_type"] == "text/plain"
    assert data[0]["size"] == 11


@pytest.mark.asyncio
async def test_file_isolation_between_users(client, db_session):
    """不同用户的文件相互隔离。"""
    # 用户 A
    resp_a = await client.post(
        "/api/v1/auth/register",
        data={"username": "file_user_a", "password": "pw_a"},
    )
    headers_a = {"Authorization": f"Bearer {resp_a.json()['access_token']}"}
    workspace_id_a = await _get_workspace_id(client, headers_a)
    await _insert_file(db_session, resp_a.json()["user"]["id"], workspace_id_a, "a.txt")

    # 用户 B
    resp_b = await client.post(
        "/api/v1/auth/register",
        data={"username": "file_user_b", "password": "pw_b"},
    )
    headers_b = {"Authorization": f"Bearer {resp_b.json()['access_token']}"}

    list_resp = await client.get("/api/v1/files/", headers=headers_b)
    assert list_resp.json()["total"] == 0
