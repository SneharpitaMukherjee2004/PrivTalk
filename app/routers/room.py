# app/routers/room.py

from fastapi import APIRouter, Cookie, Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Annotated
from sqlalchemy.orm import Session
import hashlib
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.database import SessionLocal, get_db
from app.models.user import User

router = APIRouter()

# Template engine setup
templates = Jinja2Templates(directory="app/templates")

# 🧠 Helper to generate room_id from 2 tokens (sorted then hashed)
def generate_room_id(token1: str, token2: str) -> str:
    tokens = sorted([token1.strip(), token2.strip()])
    return hashlib.sha256("".join(tokens).encode()).hexdigest()


# ✅ Route to create room (host provides 2nd user's chat_token)
@router.get("/create-room")
def create_room(
    peer_token: str,
    chat_token: str,
    db: Session = Depends(get_db)
):
    if not chat_token or not peer_token:
        return JSONResponse(content={"success": False, "message": "Missing tokens"})

    room_id = generate_room_id(chat_token, peer_token)

    # Save to DB if not already
    from app.models.chatroom import ChatRoom
    existing = db.query(ChatRoom).filter(ChatRoom.room_id == room_id).first()
    if not existing:
        new_room = ChatRoom(room_id=room_id, host_token=chat_token, peer_token=peer_token)
        db.add(new_room)
        db.commit()

    return JSONResponse(content={"success": True, "room_id": room_id})





# ✅ Route to join room (user must be valid part of room)
@router.get("/joinroom")
def joinroom_page(request: Request):
    return templates.TemplateResponse("joinroom.html", {"request": request})



# ✅ Final start-chat route (sets connect_chat cookie and redirects to /chat)
# in app/routers/room.py

from app.models.chatroom import ChatRoom

@router.get("/start-chat")
def start_chat(
    room_id: str,
    chat_token: Annotated[str, Cookie()] = None,
    db: Session = Depends(get_db)
):
    if not chat_token:
        return RedirectResponse(url="/login", status_code=302)

    # 🔍 Check if the room exists
    room = db.query(ChatRoom).filter(ChatRoom.room_id == room_id).first()
    if not room:
        return RedirectResponse(url="/joinroom?error=room_not_found", status_code=302)

    # 🔐 Check if user is allowed to join
    if chat_token not in [room.host_token, room.peer_token]:
        return RedirectResponse(url="/joinroom?error=unauthorized", status_code=302)

    # ✅ Redirect to chatroom with params
    return RedirectResponse(url=f"/chatroom?room_id={room_id}&chat_token={chat_token}")

