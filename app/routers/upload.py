from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
import uuid

router = APIRouter()

BASE_UPLOAD_DIR = "app/assets/meetings/uploads"
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

# Upload endpoint
@router.post("/upload")
async def upload_file(file: UploadFile = File(...), meeting_id: str = Form(...)):
    meeting_folder = os.path.join(BASE_UPLOAD_DIR, meeting_id)
    os.makedirs(meeting_folder, exist_ok=True)

    ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(meeting_folder, filename)

    with open(filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # ✅ This URL uses the provided meeting_id
    return {"url": f"/assets/uploads/{meeting_id}/{filename}"}


# File access endpoint
@router.get("/assets/uploads/{meeting_id}/{filename}")
async def get_uploaded_file(meeting_id: str, filename: str):
    file_path = os.path.join(BASE_UPLOAD_DIR, meeting_id, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}
