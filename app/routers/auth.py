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
from fastapi import Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form, UploadFile, File
import shutil
import os
from fastapi.responses import JSONResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="app/templates")

def hash_password_sha256(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class EmailRequest(BaseModel):
    email: EmailStr
    password: str | None = None
    username:str  | None = None

# logic for serve the Edit Profile form
@router.get("/edit-profile", response_class=HTMLResponse)
def get_edit_profile(request: Request, email: str, db: Session = Depends(get_db)):
    if not email:
        return HTMLResponse("❌ Email is required to edit profile", status_code=400)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return HTMLResponse("User not found", status_code=404)
    
    return templates.TemplateResponse("edit_profile.html", {
        "request": request,
        "username": user.username,
        "email": user.email,
        "profile_photo": user.profile_photo
    })

# Logic for handle the submission for Edit Profile
@router.post("/update-profile")
def update_profile(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(None),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        current_email = request.query_params.get("email")
        if not current_email:
            return JSONResponse(content={"error": "Missing email in query params"}, status_code=400)

        user = db.query(User).filter(User.email == current_email).first()
        if not user:
            return JSONResponse(content={"error": "User not found"}, status_code=404)

        user.username = username
        user.email = email

        if password:
            user.hashed_password = hash_password_sha256(password)

        if photo and photo.filename:
            upload_dir = "app/assets/uploads"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, photo.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            user.profile_photo = f"/assets/uploads/{photo.filename}"

        db.commit()

        return RedirectResponse(
            url=f"/profile?email={user.email}&username={user.username}&token={user.chattoken}",
            status_code=302
        )
    
    except Exception as e:
        print("🔴 UPDATE ERROR:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

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
    
# Logic for reset passord
@router.get("/reset-password-form", response_class=HTMLResponse)
def serve_reset_password_form(token: str, request: Request, db: Session = Depends(get_db)):
    token_entry = db.query(VerificationToken).filter_by(token=token).first()
    if not token_entry or token_entry.is_verified:
        return HTMLResponse("Invalid or expired reset link", status_code=400)

    return templates.TemplateResponse("reset_password.html", {
        "request": request,
        "token": token_entry.token
    })

@router.post("/submit-reset-password")
def submit_reset_password(
    request: Request,
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if new_password != confirm_password:
        return HTMLResponse("Passwords do not match", status_code=400)

    token_entry = db.query(VerificationToken).filter_by(token=token).first()
    if not token_entry or token_entry.is_verified:
        return HTMLResponse("Invalid or expired token", status_code=400)

    user = db.query(User).filter(User.email == token_entry.email).first()
    if not user:
        return HTMLResponse("User not found", status_code=404)

    hashed = hash_password_sha256(new_password)
    user.hashed_password = hashed
    db.commit()

    token_entry.is_verified = True
    db.commit()

    # ✅ Show success alert with login link
    return templates.TemplateResponse("reset_success.html", {
        "request": request
    })
    
    
#login profilepagesetup
class LoginRequest(BaseModel):
    identifier: str  # username or email
    password: str
    
@router.post("/login")
def login_user(req: LoginRequest):
    db = SessionLocal()
    try:
        # ✅ Find user by email or username
        user = db.query(User).filter(
            (User.email == req.identifier) | (User.username == req.identifier)
        ).first()

        # ❌ If no user or password mismatch
        if not user or user.hashed_password != hash_password_sha256(req.password):
            return JSONResponse(content={"success": False, "message": "Invalid credentials"})

        # ✅ Prepare JSON response
        response_data = {
            "success": True,
            "message": "Login successful",
            "email": user.email,
            "chat_token": user.chattoken,
            "username": user.username,
        }
        response = JSONResponse(content=response_data)
         
        response.set_cookie(
            key="chat_token",
            value=user.chattoken,
            httponly=True,
            path="/",
            secure=False,
            samesite="Lax"
        )
        response.set_cookie(
            key="current_user",
            value=user.username,
            httponly=True,
            samesite="Lax",
            path="/",
            secure=False,  
        )

        return response

    finally:
        db.close

from app.services.qrgenerator import create_qr_code

@router.get("/generate-qr")
def generate_qr(token: str):
    folder = "app/assets/qrcodes"
    filepath = create_qr_code(token, folder)
    filename = os.path.basename(filepath)
    return JSONResponse(content={"filename": filename})

