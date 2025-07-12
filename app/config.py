# For future configuration handling
import os
from dotenv import load_dotenv # type: ignore
QR_DIR = "app/assets/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
