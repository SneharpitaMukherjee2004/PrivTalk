from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid

router = APIRouter()
UPLOAD_DIR = "app/assets/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return {"url": f"/assets/uploads/{filename}"}

@router.get("/assets/uploads/{filename}")
async def get_uploaded_file(filename: str):
    return FileResponse(os.path.join(UPLOAD_DIR, filename))
