from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import secrets
import hashlib
from app.services.email_service import send_verification_email
from app.services.token_service import generate_token
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.token import VerificationToken
from app.models.user import User

router = APIRouter()

def hash_password_sha256(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class EmailRequest(BaseModel):
    email: EmailStr
    password: str 
    username:str

@router.post("/verify")
def verify_email(req: EmailRequest):
    try:
        token = generate_token(16)
        hashed_pass = hash_password_sha256(req.password)
        send_verification_email(req.email, token, hashed_pass,req.username)
        return {"message": "✅ Verification email sent successfully."}
    except Exception as e:
        print(f"[ERROR in /verify] {e}")  # Add this for debug
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")
    
@router.get("/verify-email")
def verify_token(token: str, request: Request):
    db: Session = SessionLocal()
    try:
        token_entry = db.query(VerificationToken).filter_by(token=token).first()
        if not token_entry:
            raise HTTPException(status_code=404, detail="Invalid or expired token.")

        if token_entry.is_verified:
            return RedirectResponse(url="/login")

        token_entry.is_verified = True
        db.commit()

        # ✅ Use the stored username
        new_user = User(
            email=token_entry.email,
            username=token_entry.username,
            hashed_password=token_entry.password,
            is_verified=True
        )
        db.add(new_user)
        db.commit()

        return RedirectResponse(url="/login")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {e}")
    finally:
        db.close()