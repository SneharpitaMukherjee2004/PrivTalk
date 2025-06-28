from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/start-chat")
def start_chat(request: Request, token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.chattoken == token).first()

    if user:
        return RedirectResponse(url=f"/chat?token={token}", status_code=302)
    else:
        return templates.TemplateResponse("connecting_new_failed.html", {
            "request": request,
            "error": "Invalid or expired chat token."
        })
