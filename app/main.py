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
# app.mount("/static", StaticFiles(directory="app/static"), name="log")

# Template engine setup
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

# Serve register.html
@app.get("/register", response_class=HTMLResponse)
def serve_login(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})