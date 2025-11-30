import os, shutil, mimetypes
from datetime import datetime

BASE_DIR = "data/files"

def save_file(uploaded_file):
    date_dir = datetime.now().strftime("%Y%m%d")
    os.makedirs(os.path.join(BASE_DIR, date_dir), exist_ok=True)
    filepath = os.path.join(BASE_DIR, date_dir, uploaded_file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    mime = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
    return filepath, mime
