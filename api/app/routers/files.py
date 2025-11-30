from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.app.services.storage import save_file
from api.app.database import get_async_session
from api.app.models import File as FileModel

router = APIRouter(prefix="/api/v1/files", tags=["Files"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), note: str = Form(None),
                      session: AsyncSession = Depends(get_async_session)):
    path, mimetype = save_file(file)
    db_file = FileModel(filename=file.filename, path=path, mimetype=mimetype, note=note)
    session.add(db_file)
    await session.commit()
    await  session.refresh(db_file)
    return {"id": db_file.id, "filename": db_file.filename, "path": db_file.path}
