from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from app.routers import auth, chat, chat_websocket, connect_new, connect_old # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi import FastAPI, Request # type: ignore
from fastapi.responses import HTMLResponse # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from app.services.qrgenerator import create_qr_code 
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import SessionLocal
from app.models.user import User
from app.routers import upload  # New router
from app.routers.auth import get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000",
    "http://localhost:8000"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(chat_websocket.router)  # register WebSocket chat route
app.include_router(connect_new.router)
app.include_router(connect_old.router)
app.include_router(upload.router)

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

#profilepage
@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, email: str, username: str, token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    qr_path = create_qr_code(token)
    qr_url = "/" + qr_path.replace("app/", "")

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

@app.get("/chat", response_class=HTMLResponse)
def serve_chat(request: Request, token: str, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.chattoken == token).all()

    if not users:
        return templates.TemplateResponse("connecting_new_failed.html", {
            "request": request,
            "error": "Invalid or expired chat token."
        })

    # ✅ FIXED: Match cookie key with actual set cookie
    current_username = request.cookies.get("current_user")  # ✅ This must match set_cookie key

    current_user_obj = db.query(User).filter(User.username == current_username).first()

    if not current_user_obj:
        return HTMLResponse("Invalid user", status_code=401)

    # ✅ Get other user
    other_user = [u for u in users if u.username != current_username][0].username

    return templates.TemplateResponse("chatting.html", {
        "request": request,
        "token": token,
        "current_user": current_user_obj.username,
        "other_user": other_user
    })



# Serve connecting_new.html page
@app.get("/connectnew", response_class=HTMLResponse)
def connect_new_user_page(request: Request):
    return templates.TemplateResponse("connecting_new.html", {"request": request})

# Serve connecting_old.html page
@app.get("/connectold", response_class=HTMLResponse)
def connect_old_user_page(request: Request):
    return templates.TemplateResponse("connecting_old.html", {"request": request})

# databaseconnection
from app.database import Base, engine
from app.models.token import VerificationToken
from app.models.message import Message
Base.metadata.create_all(bind=engine)


