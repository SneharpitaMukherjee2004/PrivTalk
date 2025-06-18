from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from app.routers import auth # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi import FastAPI, Request # type: ignore
from fastapi.responses import HTMLResponse # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
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
async def serve_profile(request: Request, email: str, token: str,username: str):
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "email": email,
        "token": token,
        "username": username
    })


#databaseconnection
from app.database import Base, engine
from app.models.token import VerificationToken
Base.metadata.create_all(bind=engine)