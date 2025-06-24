from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import secrets
import hashlib
from app.services.email_service import send_verification_email,send_reset_password
from app.services.token_service import generate_token,chat_token
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.token import VerificationToken
from app.models.user import User
from fastapi.responses import RedirectResponse

router = APIRouter()

def hash_password_sha256(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class EmailRequest(BaseModel):
    email: EmailStr
    password: str 
    username:str

#logic of verification for new user
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
            return RedirectResponse(url="/login") # type: ignore

        token_entry.is_verified = True
        db.commit()
        ctok=chat_token()
        # ✅ Use the stored username
        new_user = User(
            email=token_entry.email,
            username=token_entry.username,
            hashed_password=token_entry.password,
            chattoken=ctok
        )
        print(f"{token_entry.email}::{token_entry.username}::{token_entry.password}:::{ctok} is entered in Users")

        db.add(new_user)
        db.commit()

        return RedirectResponse(url="/login") # type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {e}")
    finally:
        db.close()
        
        
#logic of forgot password
@router.post("/resetpass")
def verify_email(req: EmailRequest):
    try:
        token = generate_token(16)
        send_reset_password(req.email,token)
        return {"message": "✅ Reset password email sent successfully."}
    except Exception as e:
        print(f"[ERROR in /resetpass] {e}")  # Add this for debug
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")
    
    
    
    
#login profilepagesetup
class LoginRequest(BaseModel):
    identifier: str  # username or email
    password: str

@router.post("/login")
def login_user(req: LoginRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            (User.email == req.identifier) | (User.username == req.identifier)
        ).first()

        if not user or user.hashed_password != hash_password_sha256(req.password):
            return {"success": False, "message": "Invalid credentials"}

        return {
            "success": True,
            "message": "Login successful",
            "email": user.email,
            "chat_token": user.chattoken,
            "username": user.username,
        }
    finally:
        db.close()
        
from fastapi.responses import JSONResponse
from app.services.qrgenerator import create_qr_code
import os

@router.get("/generate-qr")
def generate_qr(token: str):
    filepath = create_qr_code(token, folder="app/assets/qrcodes")
    filename = os.path.basename(filepath)
    return JSONResponse(content={"filename": filename})

