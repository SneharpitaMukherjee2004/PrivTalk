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
# app.mount("/static", StaticFiles(directory="static"), name="log")

@app.get("/")
def root():
    return {"message": "Welcome to PrivTalk FastAPI backend"}

# Template engine setup
templates = Jinja2Templates(directory="templates")

# Serve login.html
@app.get("/login", response_class=HTMLResponse)
def serve_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})