#services/qrfenerator.py 
import qrcode
import os
import uuid

def create_qr_code(data: str, folder: str = "app/assets/qrcodes") -> str:    
    """
    Creates a QR code from the given data and saves it in the specified folder.
    
    Args:
        data (str): The input string to encode in the QR code.
        folder (str): The folder where the QR code image will be saved (default: "qrcodes").

    Returns:
        str: The full path to the saved QR code image.
    """
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)

    # Generate a unique filename
    filename = f"qr_{uuid.uuid4().hex}.png"
    filepath = os.path.join(folder, filename)

    # Create the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filepath)

    return filepath
