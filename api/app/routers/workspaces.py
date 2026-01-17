from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models import User, Workspace, workspace_user_association
from app.schemas import (
    WorkspaceCreate,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.services.security import (
    check_workspace_permission,
    get_current_user,
    get_user_workspaces,
)

router = APIRouter(prefix="/api/v1/workspaces", tags=["Workspaces"])


@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """获取当前用户所属的所有 Workspace"""
    workspaces_roles = await get_user_workspaces(current_user, session)
    return [workspace for workspace, role in workspaces_roles]


@router.post("", response_model=WorkspaceResponse)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """创建新的 Workspace"""
    workspace = Workspace(
        name=workspace_data.name,
        description=workspace_data.description,
        created_by=current_user.id,
    )
    session.add(workspace)
    await session.commit()
    await session.refresh(workspace)

    # 将创建者设为 owner
    stmt = workspace_user_association.insert().values(
        workspace_id=workspace.id, user_id=current_user.id, role="owner"
    )
    await session.execute(stmt)
    await session.commit()

    return workspace


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """获取 Workspace 详情"""
    stmt = (
        select(Workspace, workspace_user_association.c.role)
        .join(
            workspace_user_association,
            Workspace.id == workspace_user_association.c.workspace_id,
        )
        .where(
            Workspace.id == workspace_id,
            workspace_user_association.c.user_id == current_user.id,
        )
    )
    result = await session.execute(stmt)
    workspace_role = result.first()

    if not workspace_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此 Workspace"
        )

    return workspace_role[0]


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """更新 Workspace（需要 owner 或 admin 角色）"""
    # 获取 workspace 和用户角色
    stmt = (
        select(Workspace, workspace_user_association.c.role)
        .join(
            workspace_user_association,
            Workspace.id == workspace_user_association.c.workspace_id,
        )
        .where(
            Workspace.id == workspace_id,
            workspace_user_association.c.user_id == current_user.id,
        )
    )
    result = await session.execute(stmt)
    workspace_role = result.first()

    if not workspace_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此 Workspace"
        )

    workspace, role = workspace_role
    await check_workspace_permission(workspace, role, ["owner", "admin"])

    # 更新字段
    if workspace_data.name is not None:
        workspace.name = workspace_data.name
    if workspace_data.description is not None:
        workspace.description = workspace_data.description

    await session.commit()
    await session.refresh(workspace)
    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """删除 Workspace（仅 owner 可操作）"""
    # 获取 workspace 和用户角色
    stmt = (
        select(Workspace, workspace_user_association.c.role)
        .join(
            workspace_user_association,
            Workspace.id == workspace_user_association.c.workspace_id,
        )
        .where(
            Workspace.id == workspace_id,
            workspace_user_association.c.user_id == current_user.id,
        )
    )
    result = await session.execute(stmt)
    workspace_role = result.first()

    if not workspace_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此 Workspace"
        )

    workspace, role = workspace_role
    await check_workspace_permission(workspace, role, ["owner"])

    # 删除 workspace（级联删除会处理关联）
    await session.delete(workspace)
    await session.commit()


@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberResponse])
async def list_workspace_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """获取 Workspace 成员列表"""
    # 验证用户有权限访问此 workspace
    stmt = select(workspace_user_association.c.user_id).where(
        workspace_user_association.c.workspace_id == workspace_id,
        workspace_user_association.c.user_id == current_user.id,
    )
    result = await session.execute(stmt)
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此 Workspace"
        )

    # 获取所有成员
    stmt = (
        select(
            workspace_user_association.c.workspace_id,
            workspace_user_association.c.user_id,
            User.username,
            workspace_user_association.c.role,
            workspace_user_association.c.created_at,
        )
        .join(User, workspace_user_association.c.user_id == User.id)
        .where(workspace_user_association.c.workspace_id == workspace_id)
    )
    result = await session.execute(stmt)
    members = result.all()

    return [
        WorkspaceMemberResponse(
            workspace_id=m[0], user_id=m[1], username=m[2], role=m[3], created_at=m[4]
        )
        for m in members
    ]


@router.post("/{workspace_id}/members/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_workspace_member(
    workspace_id: str,
    user_id: str,
    role: str = "member",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """添加成员到 Workspace（需要 owner 或 admin 角色）"""
    # 验证角色有效性
    valid_roles = ["owner", "admin", "member", "readonly"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的角色，必须是: {', '.join(valid_roles)}",
        )

    # 获取 workspace 和当前用户角色
    stmt = (
        select(Workspace, workspace_user_association.c.role)
        .join(
            workspace_user_association,
            Workspace.id == workspace_user_association.c.workspace_id,
        )
        .where(
            Workspace.id == workspace_id,
            workspace_user_association.c.user_id == current_user.id,
        )
    )
    result = await session.execute(stmt)
    workspace_role = result.first()

    if not workspace_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此 Workspace"
        )

    workspace, current_role = workspace_role
    await check_workspace_permission(workspace, current_role, ["owner", "admin"])

    # 检查目标用户是否存在
    user_stmt = select(User).where(User.id == user_id)
    user_result = await session.execute(user_stmt)
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 检查是否已经是成员
    check_stmt = select(workspace_user_association.c.user_id).where(
        workspace_user_association.c.workspace_id == workspace_id,
        workspace_user_association.c.user_id == user_id,
    )
    check_result = await session.execute(check_stmt)
    if check_result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户已经是成员"
        )

    # 添加成员
    stmt = workspace_user_association.insert().values(
        workspace_id=workspace_id, user_id=user_id, role=role
    )
    await session.execute(stmt)
    await session.commit()

    return {"message": "成员添加成功"}


@router.delete(
    "/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_workspace_member(
    workspace_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """从 Workspace 移除成员（需要 owner 或 admin 角色）"""
    # 获取 workspace 和当前用户角色
    stmt = (
        select(Workspace, workspace_user_association.c.role)
        .join(
            workspace_user_association,
            Workspace.id == workspace_user_association.c.workspace_id,
        )
        .where(
            Workspace.id == workspace_id,
            workspace_user_association.c.user_id == current_user.id,
        )
    )
    result = await session.execute(stmt)
    workspace_role = result.first()

    if not workspace_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此 Workspace"
        )

    workspace, current_role = workspace_role
    await check_workspace_permission(workspace, current_role, ["owner", "admin"])

    # 不能移除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不能移除自己"
        )

    # 移除成员
    stmt = delete(workspace_user_association).where(
        workspace_user_association.c.workspace_id == workspace_id,
        workspace_user_association.c.user_id == user_id,
    )
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成员不存在")
