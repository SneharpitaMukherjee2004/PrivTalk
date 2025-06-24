from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from app.routers import auth # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi import FastAPI, Request # type: ignore
from fastapi.responses import HTMLResponse # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from app.services.qrgenerator import create_qr_code 
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Mount the assets directory for QR code access
if not os.path.exists("app/assets/qrcodes"):
    os.makedirs("app/assets/qrcodes")

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
def profile_page(request: Request, email: str, username: str, token: str):
     
    qr_path = create_qr_code(token)  # returns 'app/assets/qrcodes/qr_xxxx.png'
    qr_url = "/" + qr_path.replace("app/", "")  # gives '/assets/qrcodes/qr_xxxx.png'

    # serves from /qrcodes/filename.png
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "email": email,
        "username": username,
        "token": token,
        "qr_url": qr_url
    })



# Serve connectnew.html page
@app.get("/connectnew", response_class=HTMLResponse)
def connect_new_user_page(request: Request):
    return templates.TemplateResponse("connect_new.html", {"request": request})



#databaseconnection
from app.database import Base, engine
from app.models.token import VerificationToken
Base.metadata.create_all(bind=engine)