from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.app.database import get_async_session

from api.app.models import User
from api.app.services.security import get_password_hash, verify_password

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post("/")
async def create_user(username: str, password: str, session: AsyncSession = Depends(get_async_session)):
    hashed = get_password_hash(password)
    user = User(username=username, password=hashed)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@ router.post("/me")
async def get_me(username: str, password: str, session: AsyncSession = Depends(get_async_session)):
    hashed = get_password_hash(password)
    user = User(username=username, password=hashed)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
