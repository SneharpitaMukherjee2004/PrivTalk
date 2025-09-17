
# app/services/supabase.py

from supabase import create_client, Client
import os
from typing import Optional

# Load from env (make sure these are set in your Railway/locally)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xeuvedbondlruuxnycht.supabase.co")
rawsupabasekey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhldXZlZGJvbmRscnV1eG55Y2h0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDg5MDAyOSwiZXhwIjoyMDcwNDY2MDI5fQ.nSw32mih1tctiogO4rFElw4oxw13Xl3WVB6Z7Xv0ywQ"
SUPABASE_KEY = os.getenv("SUPABASE_KEY", rawsupabasekey)
SUPABASE_BUCKET = "chat-media"
BUCKET_NAME=SUPABASE_BUCKET
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
def fillkey():
    return SUPABASE_KEY

# ========== PERSONS ==========
def upload_person_qr(person_token: str, file_path: str) -> str:
    """Upload a user's QR code safely with upsert=True."""
    file_name = f"qr_{person_token}.png"
    dest_path = f"assets/persons/{person_token}/qrcode/{file_name}"

    bucket = supabase.storage.from_(BUCKET_NAME)

    # Delete if exists
    try:
        existing = bucket.list(f"assets/persons/{person_token}/qrcode")
        if any(f['name'] == file_name for f in existing):
            bucket.remove([dest_path])
    except Exception as e:
        print("Error checking/deleting existing file:", e)

    # Upload with upsert
    try:
        bucket.upload(dest_path, file_path, {"upsert": "true"})
    except Exception as e:
        print("Upload failed:", e)
        raise e

    return get_public_url(dest_path)

def upload_person_profile_pic(person_token: str, file_path: str) -> str:
    """Upload a user's profile picture to Supabase and return public URL."""
    ext = os.path.splitext(file_path)[-1]
    dest_path = f"assets/persons/{person_token}/profilepic{ext}"

    supabase.storage.from_(SUPABASE_BUCKET).upload(
        dest_path, file_path, {"upsert": "true"}
    )
    return get_public_url(dest_path)

def get_person_qr_url(person_token: str) -> Optional[str]:
    """Fetch public URL of a person's QR code."""
    file_name = f"qr_{person_token}.png"
    path = f"assets/persons/{person_token}/qrcode/{file_name}"
    return get_public_url(path)


def get_person_profile_url(person_token: str) -> Optional[str]:
    """Fetch public URL of a person's profile picture from Supabase."""
    for ext in [".png", ".jpg", ".jpeg"]:
        path = f"assets/persons/{person_token}/profilepic{ext}"
        url = get_public_url(path)
        if url:
            return url
    return None


# ========== MEETINGS ==========
def upload_meeting_qr(meeting_id: str, file_path: str) -> str:
    """Upload a meeting's QR code into meetings/{id}/qrcode/"""
    dest_path = f"assets/meetings/{meeting_id}/qrcode/qr_{meeting_id}.png"
    print("saving meeting qr from supabase")
    supabase.storage.from_(BUCKET_NAME).upload(
        dest_path, file_path, {"upsert": "true"}  # <-- string now
    )
    return get_public_url(dest_path)


def upload_meeting_file(meeting_id: str, file_path: str) -> str:
    """Upload a chat/media file into meetings/{id}/data/"""
    file_name = os.path.basename(file_path)
    dest_path = f"assets/meetings/{meeting_id}/data/{file_name}"

    supabase.storage.from_(SUPABASE_BUCKET).upload(
        dest_path, file_path, {"upsert": True}
    )
    return get_public_url(dest_path)


def list_meeting_files(meeting_id: str):
    """List all files in a meeting's data folder."""
    prefix = f"assets/meetings/{meeting_id}/data"
    files = supabase.storage.from_(SUPABASE_BUCKET).list(prefix)
    return [get_public_url(f"{prefix}/{f['name']}") for f in files]

def delete_meeting_folder(meeting_id: str) -> None:
    """Delete all files under a meeting folder in Supabase (folders disappear automatically)."""
    prefix = f"assets/meetings/{meeting_id}"

    try:
        # Recursive listing function
        def list_recursive(path: str):
            all_files = []
            items = supabase.storage.from_(SUPABASE_BUCKET).list(path)
            for item in items:
                name = item.get("name")
                if not name:
                    continue

                full_path = f"{path}/{name}"

                # If "folder" → go deeper
                if item.get("metadata") is None:
                    all_files.extend(list_recursive(full_path))
                else:
                    all_files.append(full_path)
            return all_files

        # Get all files inside this meeting folder
        all_files = list_recursive(prefix)

        if all_files:
            supabase.storage.from_(SUPABASE_BUCKET).remove(all_files)
            print(f"✅ Deleted {len(all_files)} files under {prefix}")
        else:
            print(f"⚠️ No files found under {prefix}")

    except Exception as e:
        print(f"❌ Failed to delete meeting folder {prefix}: {e}")

# ========== UTILS ==========
def get_public_url(path: str) -> Optional[str]:
    """Return a public URL for a stored file if it exists."""
    try:
        return supabase.storage.from_(SUPABASE_BUCKET).get_public_url(path)
    except Exception:
        return None
