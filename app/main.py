from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles 
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.services.qrgenerator import create_person_qr
from app.services.supabase import get_person_qr_url
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import SessionLocal
from app.models.user import User
from app.routers import upload,auth,room,ws_chat  #routers
from app.routers.auth import get_db



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000",
    "http://localhost:8000","https://xeuvedbondlruuxnycht.storage.supabase.co/storage/v1/s3"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(room.router)
app.include_router(ws_chat.router)


app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount the assets directory for QR code access
if not os.path.exists("app/assets/qrcodes"):
    os.makedirs("app/assets/qrcodes")

app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")

# Mount the assets directory for Edit profile access
if not os.path.exists("app/assets/uploads"):
    os.makedirs("app/assets/uploads")

app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")


# Template engine setup
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

# Serve register.html
@app.get("/register", response_class=HTMLResponse)
def serve_login(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Serve login.html
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Serve forgot_password.html page
@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

# profile page
@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, email: str, username: str, token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    # create_person_qr now returns the full public URL
    qr_url = create_person_qr(token)
    qr_url=get_person_qr_url(token)
    # make sure this exists in your static folder

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "email": email,
        "username": username,
        "token": token,
        "qr_url": qr_url,
        "profile_photo": user.profile_photo if user else None
    })


# Serve for edit_profile.html page 
'''@app.get("/edit-profile", response_class=HTMLResponse)
def edit_profile_page(request: Request, email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return HTMLResponse("User not found", status_code=404)

    return templates.TemplateResponse("edit_profile.html", {
        "request": request,
        "username": user.username,
        "email": user.email,
        "profile_photo": user.profile_photo
    })'''

@app.get("/joinroom", response_class=HTMLResponse)
def serve_joinroom(request: Request, room_id: str = "", my_token: str = Query(...)):
    print(my_token,room_id)
    return templates.TemplateResponse("joinroom.html", {
        "request": request,
        "token": my_token,
        "room_id": room_id
    })

# databaseconnection
from app.database import Base, engine
from app.models.token import VerificationToken
from app.models.message import Message
Base.metadata.create_all(bind=engine)


