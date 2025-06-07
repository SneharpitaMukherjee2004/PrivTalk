# For future configuration handling
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
