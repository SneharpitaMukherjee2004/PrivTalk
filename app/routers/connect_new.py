from fastapi import APIRouter, Request, Depends, Response
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
    # 1. Get the target user using token
    user = db.query(User).filter(User.chattoken == token).first()

    # 2. Get the current user from cookie (you must already be logged in)
    current_user = request.cookies.get("current_user")

    if not current_user:
        # Not logged in
        return RedirectResponse(url="/login")

    if user:
        # 3. Just redirect without changing current_user cookie
        response = RedirectResponse(url=f"/chat?token={token}", status_code=302)
        response.set_cookie(key="chat_token", value=token, path="/")
        return response
    else:
        return templates.TemplateResponse("connecting_new_failed.html", {
            "request": request,
            "error": "Invalid or expired chat token."
        })
