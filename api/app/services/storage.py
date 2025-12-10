import os, shutil, mimetypes
from datetime import datetime

BASE_DIR = "data/files"


def _normalize_path_to_url(filepath: str) -> str:
    """将本地文件路径转换为URL友好的格式（使用/作为分隔符）"""
    return filepath.replace("\\", "/")


def save_file(uploaded_file):
    date_dir = datetime.now().strftime("%Y%m%d")
    os.makedirs(os.path.join(BASE_DIR, date_dir), exist_ok=True)
    filepath = os.path.join(BASE_DIR, date_dir, uploaded_file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    mime_type = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
    # 转换为URL友好的格式
    storage_path = _normalize_path_to_url(filepath)
    size = os.path.getsize(filepath)
    return storage_path, mime_type, size
