from pwdlib import PasswordHash

# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#hash-and-verify-the-passwords
password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models import User, Workspace, workspace_user_association
from app.services.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """验证当前用户是否为管理员"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员才能访问此资源"
        )
    return current_user


async def get_user_workspaces(
    user: User,
    session: AsyncSession,
) -> list[tuple[Workspace, str]]:
    """获取用户所属的所有 Workspace 及其角色"""
    stmt = (
        select(Workspace, workspace_user_association.c.role)
        .join(
            workspace_user_association,
            Workspace.id == workspace_user_association.c.workspace_id,
        )
        .where(workspace_user_association.c.user_id == user.id)
    )
    result = await session.execute(stmt)
    return result.all()


async def get_current_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> tuple[Workspace, str]:
    """获取当前 Workspace 并验证用户权限，返回 (Workspace, role)"""
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

    return workspace_role


async def check_workspace_permission(
    workspace: Workspace, user_role: str, required_roles: list[str]
) -> None:
    """检查用户在 Workspace 中的角色权限"""
    if user_role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"需要以下角色之一: {', '.join(required_roles)}",
        )


async def get_user_default_workspace(
    user: User,
    session: AsyncSession,
) -> str:
    """获取用户的默认 Workspace ID（第一个加入的 Workspace）"""
    stmt = (
        select(Workspace.id)
        .join(
            workspace_user_association,
            Workspace.id == workspace_user_association.c.workspace_id,
        )
        .where(workspace_user_association.c.user_id == user.id)
        .order_by(workspace_user_association.c.created_at)
        .limit(1)
    )
    result = await session.execute(stmt)
    workspace_id = result.scalar_one_or_none()

    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户没有加入任何 Workspace"
        )

    return workspace_id
