# app/services/qrgenerator.py

import qrcode
import os
from . import supabase

def create_person_qr(person_token: str) -> str:
    """
    Generate a QR code for a person and upload it to Supabase.
    Returns the public URL of the QR code.
    """
    # Local folder inside project (Windows-safe)
    person_dir = os.path.join("chat-media", "assets", "persons", person_token, "qrcode")
    os.makedirs(person_dir, exist_ok=True)

    file_name = f"qr_{person_token}.png"
    local_path = os.path.join(person_dir, file_name)

    # Generate QR code
    img = qrcode.make(person_token)
    img.save(local_path)

    # Upload to Supabase
    url = supabase.upload_person_qr(person_token, local_path)

    # Optional: keep the local file, or delete if you want
    os.remove(local_path)

    return url
# app/services/qrgenerator.py
import qrcode
import os

def create_meeting_qr(meeting_id: str) -> str:
    """
    Generates a QR code for a meeting and returns the relative path.
    """
    # Define folder path
    folder_path = os.path.join("assets", "meetings", meeting_id)
    os.makedirs(folder_path, exist_ok=True)

    # Define QR file path
    local_qr_file= os.path.join(folder_path, f"qr_{meeting_id}.png")

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(meeting_id)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    print("saving meetinng qr from qrgenerator")
    img.save(local_qr_file)
    url = supabase.upload_meeting_qr(meeting_id, local_qr_file)
    os.remove(local_qr_file)
    # Return relative path for frontend use
    return url
