from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models import SystemAdmin, User, Workspace, workspace_user_association
from app.services.jwt import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.services.security import (
    get_current_user,
    get_password_hash,
    is_system_admin,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register")
async def register(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    username = form_data.username
    password = form_data.password
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已经存在"
        )

    # 检查是否为第一位用户
    count_stmt = select(User)
    count_result = await session.execute(count_stmt)
    user_count = len(count_result.scalars().all())
    is_first_user = user_count == 0

    hashed_password = get_password_hash(password)
    user = User(username=username, password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # 第一位用户自动添加到系统管理员表
    if is_first_user:
        system_admin = SystemAdmin(user_id=user.id, granted_by=None)
        session.add(system_admin)
        await session.commit()

    # 创建第一个 Workspace 并将用户设为 owner
    workspace = Workspace(
        name=f"{username}'s Workspace",
        description="Default Workspace",
        created_by=user.id,
    )
    session.add(workspace)
    await session.commit()
    await session.refresh(workspace)

    # 建立用户与 Workspace 的关系，角色为 owner
    stmt = workspace_user_association.insert().values(
        workspace_id=workspace.id, user_id=user.id, role="owner"
    )
    await session.execute(stmt)
    await session.commit()

    access_token = create_access_token(subject=user.username)
    refresh_token = create_refresh_token(subject=user.username)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=False,
    )

    # 检查是否为系统管理员
    is_admin = await is_system_admin(user.id, session)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "is_system_admin": is_admin},
    }


@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    username = form_data.username
    password = form_data.password
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    access_token = create_access_token(subject=user.username)
    refresh_token = create_refresh_token(subject=user.username)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=False,
    )

    # 检查是否为系统管理员
    is_admin = await is_system_admin(user.id, session)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "is_system_admin": is_admin},
    }


@router.get("/me")
async def read_current_user(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """获取当前用户信息，包括是否为系统管理员"""
    is_admin = await is_system_admin(current_user.id, session)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_system_admin": is_admin,
    }


@router.get("/is-system-admin")
async def check_is_system_admin(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """检查当前用户是否为系统管理员"""
    is_admin = await is_system_admin(current_user.id, session)
    return {"is_system_admin": is_admin}


@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_async_session),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少 refresh token"
        )
    try:
        payload = decode_token(refresh_token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="无效 refresh token"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效 refresh token"
        )
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在"
        )
    access_token = create_access_token(subject=user.username)
    new_refresh_token = create_refresh_token(subject=user.username)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=False,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username},
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token")
    return {"message": "退出成功"}
