from fastapi import APIRouter, Form, Request, Depends
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

@router.post("/connectold")
def connect_old_user(request: Request, username: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if user:
        return RedirectResponse(url=f"/chat?token={user.chattoken}", status_code=302)
    else:
        return templates.TemplateResponse("connecting_old_failed.html", {
            "request": request,
            "error": "Username not found. Please try again."
        })
