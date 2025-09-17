
# app/services/supabase.py
import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xeuvedbondlruuxnycht.supabase.co")
rawsupabasekey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhldXZlZGJvbmRscnV1eG55Y2h0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDg5MDAyOSwiZXhwIjoyMDcwNDY2MDI5fQ.nSw32mih1tctiogO4rFElw4oxw13Xl3WVB6Z7Xv0ywQ"
SUPABASE_KEY = os.getenv("SUPABASE_KEY", rawsupabasekey)
BUCKET_NAME = "chat-media"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def _make_public_url(path: str) -> str:
    """
    Builds the public URL for a given Supabase storage path.
    """
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{path}"


def upload_file(file_bytes: bytes, path: str, content_type: str = "application/octet-stream") -> str:
    """
    Upload a file to Supabase bucket and return its public URL.
    If file already exists, it is overwritten.
    """
    try:
        # remove if already exists (to avoid duplication errors)
        try:
            supabase.storage.from_(BUCKET_NAME).remove([path])
        except Exception:
            pass

        supabase.storage.from_(BUCKET_NAME).upload(path, file_bytes, {"content-type": content_type})
        return _make_public_url(path)
    except Exception as e:
        raise RuntimeError(f"Upload failed for {path}: {str(e)}")


def delete_path(path: str) -> bool:
    """
    Delete a file or folder from Supabase bucket.
    Returns True if deleted, False otherwise.
    """
    try:
        response = supabase.storage.from_(BUCKET_NAME).remove([path])
        if response and isinstance(response, list) and "error" in response[0]:
            return False
        return True
    except Exception as e:
        print(f"Supabase delete failed: {e}")
        return False


def list_files(folder: str) -> list:
    """
    List all files under a given folder.
    """
    try:
        return supabase.storage.from_(BUCKET_NAME).list(folder)
    except Exception as e:
        print(f"Supabase list failed: {e}")
        return []


def fillkey():
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhldXZlZGJvbmRscnV1eG55Y2h0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDg5MDAyOSwiZXhwIjoyMDcwNDY2MDI5fQ.nSw32mih1tctiogO4rFElw4oxw13Xl3WVB6Z7Xv0ywQ"
    return SUPABASE_KEY
SUPABASE_KEY = fillkey()