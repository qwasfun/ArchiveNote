from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.app.database import get_async_session

from api.app.models import Note

router = APIRouter(prefix="/api/v1/notes", tags=["Notes"])


@router.post("/")
async def create_note(title: str, content: str, session: AsyncSession = Depends(get_async_session)):
    note = Note(title=title, content=content)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note
