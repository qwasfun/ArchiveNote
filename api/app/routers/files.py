import shutil
import os
import uuid
from typing import List, Optional
from urllib.parse import quote
from fastapi import APIRouter, UploadFile, Depends, HTTPException, File as FastAPIFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from api.app.database import get_async_session
from api.app.models import File
from api.app.services.security import get_current_user
from api.app.schemas import FileResponseModel
from fastapi.responses import FileResponse
from api.app.models import User
from datetime import datetime
from api.app.services.storage import save_file

router = APIRouter(prefix="/api/v1/files", tags=["Files"])

UPLOAD_DIR = "data/uploads"


@router.post("/", response_model=List[FileResponseModel])
async def upload_files(
        files: List[UploadFile] = FastAPIFile(...),
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    results = []
    for file in files:
        # # Generate safe filename
        # ext = os.path.splitext(file.filename)[1]
        # unique_name = f"{uuid.uuid4()}{ext}"
        # file_path = os.path.join(UPLOAD_DIR, unique_name)

        # # Save to disk
        # with open(file_path, "wb") as buffer:
        #     shutil.copyfileobj(file.file, buffer)

        # # Get size
        # size = os.path.getsize(file_path)

        storage_path, mime_type, size = save_file(file)

        # Save to DB
        new_file = File(
            user_id=current_user.id,
            filename=file.filename,
            storage_path=storage_path,
            mime_type=mime_type,
            size=size,
            created_at=datetime.now()
        )
        db.add(new_file)
        results.append(new_file)
        # Flush to get ID if needed immediately, but we commit at the end of loop or batched?
        # Actually commit each for safety in MVP or gathered. Let's add to session.

    await db.commit()
    for result in results:
        await db.refresh(result)
    return results


@router.get("/")
async def list_files(
        q: Optional[str] = None,
        page: int = Query(1, ge=1, description="页码，从1开始"),
        page_size: int = Query(10, ge=1, le=100, description="每页条数，默认10"),
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    """获取当前用户的文件列表（分页）"""

    # 计算偏移量
    offset = (page - 1) * page_size

    stmt = select(File).where(File.user_id == current_user.id)

    if q:
        stmt = stmt.where(File.filename.ilike(f"%{q}%"))

    query = stmt.offset(offset).limit(page_size).order_by(
        File.created_at.desc()
    )

    # 获取总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    # 获取分页数据

    result = await db.execute(query)
    files = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": [
            {
                "id": f.id,
                "filename": f.filename,
                "size": f.size,
                "storage_path": f.storage_path,
                "download_url": f"api/v1/files/download/{f.id}/{f.filename}",
                "mime_type": f.mime_type,
                "created_at": f.created_at
            }
            for f in files
        ]
    }


@router.get("/{file_id}", response_model=FileResponseModel)
async def get_file_metadata(file_id: str, db: AsyncSession = Depends(get_async_session),
                            current_user: User = Depends(get_current_user)):
    result = await db.execute(select(File).where((File.id == file_id) & (File.user_id == current_user.id)))
    file = result.scalar_one_or_none()
    file.download_url = f"api/v1/files/download/{file.id}/{file.filename}",
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


@router.delete("/{file_id}")
async def delete_file(file_id: str, db: AsyncSession = Depends(get_async_session),
                      current_user: User = Depends(get_current_user)):
    result = await db.execute(select(File).where((File.id == file_id) & (File.user_id == current_user.id)))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete from disk
    file_path = os.path.join(UPLOAD_DIR, file.storage_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete from DB
    await db.delete(file)
    await db.commit()
    return {"message": "File deleted"}


@router.get("/download/{file_id}/{filename}")
async def download_file(
        file_id: str,
        filename: Optional[str] = None,
        session: AsyncSession = Depends(get_async_session),
):
    """下载文件"""

    # 查询文件
    stmt = select(File).where(
        (File.id == file_id)
    )
    result = await session.execute(stmt)
    file_record = result.scalar_one_or_none()

    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在或无权限访问")

    # 检查文件是否存在
    storage_path = file_record.storage_path
    if not os.path.exists(storage_path):
        raise HTTPException(status_code=404, detail="文件在服务器上不存在")

    # 如果是PDF文件,使用inline方式在浏览器中显示
    if file_record.mime_type == "application/pdf":
        # 对文件名进行URL编码以支持中文等非ASCII字符
        encoded_filename = quote(file_record.filename)
        return FileResponse(
            path=storage_path,
            filename=file_record.filename,
            media_type=file_record.mime_type,
            headers={"Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}"}
        )
    
    return FileResponse(
        path=storage_path,
        filename=file_record.filename,
        media_type=file_record.mime_type
    )
