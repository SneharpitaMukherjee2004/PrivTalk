#services/qrfenerator.py 
import qrcode
import os
import uuid

def create_qr_code(data: str, folder: str = "app/assets/qrcodes/persons") -> str:
    """
    Creates a QR code for the given data only if it doesn't already exist.
    Returns the path to the QR code image.
    """
    os.makedirs(folder, exist_ok=True)

    # ✅ Use token-based filename instead of random UUID
    safe_token = data.replace("/", "_")  # if your token might include unsafe characters
    filename = f"qr_{safe_token}.png"
    filepath = os.path.join(folder, filename)

    # ✅ Skip generation if file already exists
    if os.path.exists(filepath):
        return filepath

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filepath)

    return filepath
