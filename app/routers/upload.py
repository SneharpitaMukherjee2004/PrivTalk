
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
import uuid

router = APIRouter()

# Base directory for meeting uploads
BASE_UPLOAD_DIR = "app/assets/meetings/uploads"
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

# ✅ Upload endpoint for any file type
@router.post("/upload")
async def upload_file(file: UploadFile = File(...), meeting_id: str = Form(...)):
    meeting_folder = os.path.join(BASE_UPLOAD_DIR, meeting_id)
    os.makedirs(meeting_folder, exist_ok=True)

    # Keep original extension
    ext = file.filename.split('.')[-1] if '.' in file.filename else ""
    filename = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())
    filepath = os.path.join(meeting_folder, filename)

    # Save the file
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())

    return {
        "message": "File uploaded successfully",
        "url": f"/assets/uploads/{meeting_id}/{filename}"
    }

# ✅ Endpoint to serve uploaded files
@router.get("/assets/uploads/{meeting_id}/{filename}")
async def get_uploaded_file(meeting_id: str, filename: str):
    file_path = os.path.join(BASE_UPLOAD_DIR, meeting_id, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    return {"error": "File not found"}