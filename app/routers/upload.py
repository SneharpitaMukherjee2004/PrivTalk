
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
import uuid
from app.routers.data import fillkey 
router = APIRouter()
"""
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
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from supabase import create_client
from sqlalchemy.orm import Session
import uuid
from io import BytesIO
from app.database import get_db
from app.models.chatroom import ChatRoom

router = APIRouter()

# 🔹 Supabase credentials
SUPABASE_URL = "https://xeuvedbondlruuxnycht.supabase.co"
SUPABASE_KEY = fillkey()
BUCKET_NAME = "chat-media"  # Make sure bucket exists in Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Upload endpoint
@router.post("/upload")
async def upload_file(file: UploadFile = File(...), meeting_id: str = Form(...)):
    # Keep original extension
    ext = file.filename.split('.')[-1] if '.' in file.filename else ""
    filename = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())

    # Supabase "folder" path
    storage_path = f"{meeting_id}/{filename}"

    file_content = await file.read()

    # Upload to Supabase
    supabase.storage.from_(BUCKET_NAME).upload(
        path=storage_path,
        file=file_content,
        file_options={"content-type": file.content_type}
    )

    # Public file URL
    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)

    return {"message": "File uploaded successfully", "url": public_url}


def list_all_files(bucket, folder):
    """Recursively list all files in a Supabase folder."""
    all_files = []
    stack = [folder]
    while stack:
        current = stack.pop()
        items = bucket.list(path=current)
        for item in items:
            if item.get("metadata") is None:
                # It's a folder
                stack.append(f"{current}/{item['name']}")
            else:
                # It's a file
                all_files.append(f"{current}/{item['name']}")
    return all_files

@router.post("/terminate-room")
async def terminate_room(room_id: str = Form(...), db: Session = Depends(get_db)):
    room = db.query(ChatRoom).filter(ChatRoom.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Delete QR code locally
    qr_path = f"app/assets/qrcodes/{room_id}.png"
    if os.path.exists(qr_path):
        os.remove(qr_path)

    # Delete all Supabase files (including nested)
    files_to_delete = list_all_files(supabase.storage.from_(BUCKET_NAME), room_id)
    if files_to_delete:
        supabase.storage.from_(BUCKET_NAME).remove(files_to_delete)

    # Delete DB record
    db.delete(room)
    db.commit()

    return {"message": "Room terminated successfully"}
