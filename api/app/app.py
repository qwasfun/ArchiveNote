from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api.app.database import create_db_and_tables, get_async_session
from api.app.models import Note as NotesModel

from sqlalchemy.ext.asyncio import AsyncSession

from contextlib import asynccontextmanager

from api.app.routers import files, notes
from api.app.schemas import Note


# from api.app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


# app = FastAPI(title="File & Note System")
app = FastAPI(lifespan=lifespan)

app.include_router(files.router)
app.include_router(notes.router)


# app.include_router(immich.router)

@app.get("/api/hello")
async def hello():
    return {"message": "Hello World"}


# 前端静态目录
dist_path = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")


# SPA 路由 fallback，保证前端路由可用
@app.get("/{full_path:path}")
def spa(full_path: str):
    index = dist_path / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"error": "index.html not found"}
