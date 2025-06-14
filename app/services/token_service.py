#token_service.py
import secrets

def generate_token(length: int = 16) -> str:
    return secrets.token_urlsafe(length)


#dbverification
from app.database import SessionLocal
from app.models.token import VerificationToken

def save_token_to_db(email: str, token: str):
    db = SessionLocal()
    try:
        vt = VerificationToken(email=email, token=token)
        db.add(vt)
        db.commit()
        db.refresh(vt)
        return vt
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()