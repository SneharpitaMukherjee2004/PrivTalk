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
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import hashlib
import qrcode
import os

from app.models.user import User
from app.models.chatroom import ChatRoom
from app.database import get_db
from app.config import QR_DIR 

router = APIRouter()


def generate_room_id(token1: str, token2: str) -> str:
    tokens = sorted([token1.strip(), token2.strip()])
    return hashlib.sha256("".join(tokens).encode()).hexdigest()


def generate_room_qr(room_id: str) -> str:
    qr_path = os.path.join(QR_DIR, f"{room_id}.png")
    if not os.path.exists(qr_path):
        img = qrcode.make(room_id)
        img.save(qr_path)
    return f"/assets/qrcodes/{room_id}.png"


@router.get("/create-room")
def create_room(
    chat_token: str = Query(...),
    peer_token: str = Query(...),
    db: Session = Depends(get_db)
):
    # 🔐 Validation
    if not chat_token or not peer_token:
        return RedirectResponse(url="/profile?error=missing_tokens", status_code=302)

    room_id = generate_room_id(chat_token, peer_token)

    # 🗃️ Save to DB only if not exists
    existing = db.query(ChatRoom).filter(ChatRoom.room_id == room_id).first()
    if not existing:
        new_room = ChatRoom(room_id=room_id, host_token=chat_token, peer_token=peer_token)
        db.add(new_room)
        db.commit()

    # 🧾 Generate QR code
    qr_url = generate_room_qr(room_id)

    # 🚀 Redirect to chatroom with room ID and QR link
    return RedirectResponse(
        url=f"/chatroom?room_id={room_id}&qr_url={qr_url}",
        status_code=302
    )



# ✅ Route to join room (user must be valid part of room)
@router.get("/joinroom")
def joinroom_page(request: Request):
    return templates.TemplateResponse("joinroom.html", {"request": request})

from fastapi import Form

@router.post("/attempt-join")
def attempt_join(
    request: Request,
    room_id: str = Form(...),
    chat_token: str = Form(...),
    db: Session = Depends(get_db)
):
    from app.models.chatroom import ChatRoom
    room = db.query(ChatRoom).filter(ChatRoom.room_id == room_id).first()

    if not room:
        return templates.TemplateResponse("joinroom.html", {
            "request": request,
            "error": "Room not found",
        })

    if chat_token == room.host_token or chat_token == room.peer_token:
        # ✅ Redirect to chatroom
        return RedirectResponse(
            url=f"/chatroom?room_id={room_id}&chat_token={chat_token}",
            status_code=302
        )

    return templates.TemplateResponse("joinroom.html", {
        "request": request,
        "error": "Access Denied",
    })

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

from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="app/templates")

@router.get("/chatroom")
def chatroom(
    request: Request,
    room_id: str,
    qr_url: str = "",
    db: Session = Depends(get_db)
):
    # Lookup the room
    room = db.query(ChatRoom).filter(ChatRoom.room_id == room_id).first()
    if not room:
        return RedirectResponse(url="/profile?error=room_not_found", status_code=302)

    # Get host user details using host_token
    user = db.query(User).filter(User.chattoken == room.host_token).first()
    print(user)
    return templates.TemplateResponse("chatroom.html", {
        "request": request,
        "room_id": room_id,
        "qr_url": qr_url,
        "username": user.username,
        "email": user.email,
        "token": user.chattoken
    })
